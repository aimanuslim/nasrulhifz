from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

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
	windexform = WordIndexForm(request.POST)
	print(request.POST.getlist('index'))
	print(windexform)

	

	if hifzform.is_valid():
		hifz = Hifz(surah_number=request.POST['surah_number'], ayat_number=request.POST['ayat_number'])
		# find surah ayat limits and ayat words limits
		ayat_limit, wordindex_limit = findMeta(hifz.surah_number, hifz.ayat_number)
		if int(hifz.ayat_number) <= ayat_limit:
			hifz.save()
			message = 'Submission successful'
		else:
			raise Http404('Ayat number exceeds')



	else:
		raise Http404('Ayat limit exceeded')
	return render(request, 'qurandata/index.html', {'message': message, 'latest_quran_data' : Hifz.objects.values('surah_number').distinct() })

def enter(request):
	hifzform = HifzForm(request.GET or None)
	wiform = WordIndexForm(request.GET or None)
	wiformset = WordIndexFormSet(request.GET or None)
	return render(request, 'qurandata/enter.html', {'hifzform': hifzform, 'wiform': wiform, 'wiformset': wiformset})


def detail(request, surah_number, ayat_number):
	print("{} {}".format(surah_number, ayat_number))
	qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
	if len(qm) == 1:
		qm = qm[0]
		
	else:
		raise Http404("Quran String was not found for surah {} ayat {}".format(surah_number, ayat_number))
	return render(request, 'qurandata/detail.html', {'quranmeta': qm})

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

