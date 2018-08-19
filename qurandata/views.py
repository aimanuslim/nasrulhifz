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

def enter(request):

    if request.method == 'GET':
        hifzform = HifzForm(request.GET or None)
        if request.GET.get('surah_number') and request.GET.get('ayat_number'):
            data = return_ayat_details(request.GET['surah_number'], request.GET['ayat_number'])
            data['hifzform'] = hifzform
            print("Data {}".format(data))
            return render(request, 'qurandata/enter.html', data)
        else:
            return render(request, 'qurandata/enter.html', { 'hifzform': hifzform })


    if request.method == 'POST':
        hifzform = HifzForm(request.POST)
        surah_number = request.POST['surah_number']
        ayat_number = request.POST['ayat_number']

        if hifzform.is_valid():
            ayat_limit = findMetaSurah(surah_number)
            if int(ayat_number) <= ayat_limit:
                save_word_index_difficulty(request, surah_number, ayat_number)
                message = 'Submission successful'
                messages.success(request, message, extra_tags='alert alert-success')
            else:
                message = "Ayat number exceeds limit for surah"
                messages.warning(request, message, extra_tags='alert alert-danger')
        else:
            message = "Ayat number exceeds limit for surah"
            messages.warning(request, message, extra_tags='alert alert-danger')

        return HttpResponseRedirect("")

def get_string_table_type_from_difficulty(level):
    if level == 1: return "table-danger"
    if level == 2: return "table-primary"
    if level == 3: return "table-success"

def return_ayat_details(surah_number, ayat_number):
    qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
    if len(qm) == 1:
        qm = qm[0]

    else:
        raise Http404("Quran String was not found for surah {} ayat {}".format(surah_number, ayat_number))

    to_display = qm.ayat_string.split(" ")
    form_meta = {}
    display_meta = []
    for i, disp in enumerate(to_display):
        form_meta["class-word-" + str(i)] = "word-" + str(i)
        display_meta.append("class-word-" + str(i))

    hifz_query = Hifz.objects.filter(surah_number=surah_number, ayat_number=ayat_number)

    if hifz_query:
        wordindexset = hifz_query[0].wordindex_set.all()
        print(len(wordindexset))
        tablecolorset = [get_string_table_type_from_difficulty(w.difficulty) for w in wordindexset]
        wordindexsetdifficulties = [w.difficulty for w in wordindexset]
    else:
        tablecolorset = [get_string_table_type_from_difficulty(3) for w in range(0, len(to_display))]
        wordindexsetdifficulties = [3 for w in range(0, len(to_display))]

    print(tablecolorset, wordindexsetdifficulties)

    display_with_meta = (to_display, display_meta, tablecolorset, wordindexsetdifficulties)

    data = {'display_with_meta': display_with_meta}
    return data

def save_word_index_difficulty(request, surah_number, ayat_number):
    hifz = Hifz.objects.filter(surah_number=surah_number, ayat_number=ayat_number)

    if hifz:
        hifz = hifz[0]
        wset = hifz.wordindex_set.all()
        len_wset = len(wset)
    else:
        hifz = Hifz(surah_number=surah_number, ayat_number=ayat_number)
        hifz.save()
        qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
        qm = qm[0]
        len_wset = len(qm.ayat_string.split(" "))
        wset = None

    for i in range(0, len_wset):
        wordindex_difficulty = request.POST.get("class-word-" + str(i))
        if not wordindex_difficulty: wordindex_difficulty = 3

        if wset:
            w = wset.filter(index=i)
            w = w[0]
            print("Index {} Old Difficulty {} New Difficulty {}".format(w.index, w.difficulty, wordindex_difficulty))
            w.difficulty = int(wordindex_difficulty)
            w.save()
        else:
            print("Creating new word indices")
            WordIndex(index=i, difficulty=int(wordindex_difficulty), hifz=hifz).save()


def detail(request, surah_number, ayat_number):
    data = return_ayat_details(surah_number,ayat_number)

    if request.method == 'GET':
        print(data)
        return render(request, 'qurandata/detail.html', data)


    if request.method == 'POST':
        save_word_index_difficulty(request=request, surah_number=surah_number, ayat_number=ayat_number)

        message = "Word difficulties updated."
        messages.success(request, message)
        return HttpResponseRedirect("")



def findMetaAyat(surah_number, ayat_number):
    qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
    if len(qm) == 1:
        qm = qm[0]
    else:
        return None
    wordindex_limit = len(qm.ayat_string.split(" "))
    return wordindex_limit

def findMetaSurah(surah_number):
    ayat_limit = len(QuranMeta.objects.filter(surah_number=surah_number))
    return ayat_limit


# def index(request):
#     latest_quran_data = Hifz.objects.order_by('-surah_number')[:5]
#     context = {
#         'latest_quran_data': latest_quran_data,
#     }
#     return render(request, 'qurandata/index.html', context)

# def detail(request, hifz_id):
# 	hifz = get_object_or_404(Hifz, pk=hifz_id)
# 	return render(request, 'qurandata/detail.html', {'hifz': hifz})

