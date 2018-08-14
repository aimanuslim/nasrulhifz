from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from django.contrib import messages

from .models import Hifz, QuranMeta, WordIndex
from .forms import HifzForm, WordIndexForm, WordIndexFormSet

class IndexView(generic.ListView):
	template_name = 'qurandata/index.html'
	context_object_name = 'latest_quran_data'

	def get_queryset(self):
		return Hifz.objects.values('surah_number').distinct()

class AyatListView(generic.ListView):
	template_name = 'qurandata/ayatlist.html'
	context_object_name = 'ayat_list_for_surah'

	def get_queryset(self):
		# hifz = get_object_or_404(Hifz, pk=self.kwargs['pk'])
		# return Hifz.objects.filter(surah_number=hifz.surah_number)
		return Hifz.objects.filter(surah_number=self.kwargs['surah_number']).values('surah_number', 'ayat_number').distinct()

def submit(request):
	hifzform = HifzForm(request.POST)
	windexformset = WordIndexFormSet(request.POST)

	

	if hifzform.is_valid():
		hifz = Hifz(surah_number=request.POST['surah_number'], ayat_number=request.POST['ayat_number'])
		# find surah ayat limits and ayat words limits
		ayat_limit, wordindex_limit = findMeta(hifz.surah_number, hifz.ayat_number)
		if int(hifz.ayat_number) <= ayat_limit:
			hifz.save()
			message = 'Submission successful'

		else:
			raise Http404('Ayat number exceeds')

		if windexformset.is_valid():
			for wiform in windexformset:
				index = wiform.cleaned_data.get('index')
				if index <= wordindex_limit:
					WordIndex(index=index,hifz=hifz).save()
				else:
					raise Http404("Word index limit exceeded")
		else:
			raise Http404("Word index data invalid")


	else:
		raise Http404('Ayat limit exceeded')
	messages.success(request, message)
	return HttpResponseRedirect("qurandata/enter.html")
	# return render(request, 'qurandata/index.html', {'message': message, 'latest_quran_data' : Hifz.objects.values('surah_number').distinct() })

def enter(request):

	if request.method == 'GET':
		hifzform = HifzForm(request.GET or None)
		wiform = WordIndexForm(request.GET or None)
		wiformset = WordIndexFormSet(request.GET or None)
		return render(request, 'qurandata/enter.html', {'hifzform': hifzform, 'wiform': wiform, 'wiformset': wiformset})

	if request.method == 'POST':
		hifzform = HifzForm(request.POST)
		windexformset = WordIndexFormSet(request.POST)

		if hifzform.is_valid():
			hifz = Hifz(surah_number=request.POST['surah_number'], ayat_number=request.POST['ayat_number'])
			# find surah ayat limits and ayat words limits
			ayat_limit, wordindex_limit = findMeta(hifz.surah_number, hifz.ayat_number)
			if int(hifz.ayat_number) <= ayat_limit:
				hifz.save()
				message = 'Submission successful'

			else:
				raise Http404('Ayat number exceeds')

			if windexformset.is_valid():
				for wiform in windexformset:
					index = wiform.cleaned_data.get('index')
					if index <= wordindex_limit:
						WordIndex(index=index,hifz=hifz).save()
					else:
						raise Http404("Word index limit exceeded")
			else:
				raise Http404("Word index data invalid")


		else:
			raise Http404('Ayat limit exceeded')
		messages.success(request, message)
		return HttpResponseRedirect("")


def detail(request, surah_number, ayat_number):
	qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
	if len(qm) == 1:
		qm = qm[0]

	else:
		raise Http404("Quran String was not found for surah {} ayat {}".format(surah_number, ayat_number))

	to_display = qm.ayat_string.split(" ")[::-1]
	form_meta = {}
	display_meta = []
	for i, disp in enumerate(to_display):
		form_meta["class-word-" + str(i)] = "word-" + str(i)
		display_meta.append("class-word-" + str(i))


	if request.method == 'GET':	
		data = {'quranmeta': qm, 'splitted_ayat': to_display, 'form_meta': form_meta, 'display_meta': display_meta}
		return render(request, 'qurandata/detail.html', data)


	if request.method == 'POST':
		# data = {'quranmeta': qm, 'splitted_ayat':  display_meta, 'form_meta': form_meta, 'display_meta': display_meta, 'message': "Word difficulties updated."}
		hifz = Hifz.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
		hifz = hifz[0]
		wset = hifz.wordindex_set.all()
		for i in range(len(to_display)):
			wordindex_difficulty = request.POST["class-word-" + str(i)]
			if wset:
				w = wset.filter(index=i)
				w = w[0]
				w.difficulty = int(wordindex_difficulty)
				# print("Index {} Difficulty {}".format(w[0].index, w[0].difficulty))
				w.save()
			else:
				print("Creating new word indices")
				WordIndex(index=i, difficulty=int(wordindex_difficulty), hifz=hifz).save()

		message = "Word difficulties updated."
		messages.success(request, message)
		return HttpResponseRedirect("")




def findMeta(surah_number, ayat_number):
	ayat_limits = len(QuranMeta.objects.filter(surah_number=surah_number))
	qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
	if len(qm) == 1:
		qm = qm[0]
	else:
		return None, None
	wordindex_limits = len(qm.ayat_string.split(" "))
	return ayat_limits, wordindex_limits


# def index(request):
#     latest_quran_data = Hifz.objects.order_by('-surah_number')[:5]
#     context = {
#         'latest_quran_data': latest_quran_data,
#     }
#     return render(request, 'qurandata/index.html', context)

# def detail(request, hifz_id):
# 	hifz = get_object_or_404(Hifz, pk=hifz_id)
# 	return render(request, 'qurandata/detail.html', {'hifz': hifz})

