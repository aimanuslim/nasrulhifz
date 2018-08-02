from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Hifz


def index(request):
    latest_quran_data = Hifz.objects.order_by('-surah_number')[:5]
    context = {
        'latest_quran_data': latest_quran_data,
    }
    return render(request, 'qurandata/index.html', context)

def detail(request, hifz_id):
	hifz = get_object_or_404(Hifz, pk=hifz_id)
	return render(request, 'qurandata/detail.html', {'hifz': hifz})

