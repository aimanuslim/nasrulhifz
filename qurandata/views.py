from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Hifz, QuranMeta
from .forms import HifzForm
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
	form = HifzForm(request.POST)
	if form.is_valid():
		hifz = Hifz(surah_number=request.POST['surah_number'], ayat_number=request.POST['ayat_number'])
		hifz.save()
		message = 'Submission successful'
	else:
		message = 'Submission failed'
	return render(request, 'qurandata/index.html', {'message': message, 'latest_quran_data' : Hifz.objects.values('surah_number').distinct() })


def detail(request, surah_number, ayat_number):
	print("{} {}".format(surah_number, ayat_number))
	qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
	if len(qm) == 1:
		qm = qm[0]
		
	else:
		raise Http404("Quran String was not found for surah {} ayat {}".format(surah_number, ayat_number))
	return render(request, 'qurandata/detail.html', {'quranmeta': qm})


# def index(request):
#     latest_quran_data = Hifz.objects.order_by('-surah_number')[:5]
#     context = {
#         'latest_quran_data': latest_quran_data,
#     }
#     return render(request, 'qurandata/index.html', context)

# def detail(request, hifz_id):
# 	hifz = get_object_or_404(Hifz, pk=hifz_id)
# 	return render(request, 'qurandata/detail.html', {'hifz': hifz})

