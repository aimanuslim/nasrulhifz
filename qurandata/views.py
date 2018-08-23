from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from django.contrib import messages

from .models import Hifz, QuranMeta, WordIndex, SurahMeta
from .forms import HifzForm, WordIndexForm, WordIndexFormSet

class IndexView(generic.ListView):
    template_name = 'qurandata/index.html'
    context_object_name = 'latest_quran_data'

    def get_queryset(self):
        hifz_list = Hifz.objects.order_by('surah_number').values('surah_number').distinct()
        if len(hifz_list) == 0:
            return None

        surah_meta_list = []
        for hifz in hifz_list:
            surah_meta = SurahMeta.objects.filter(surah_number=int(hifz.get('surah_number')))
            surah_meta = surah_meta[0]
            surah_meta_list.append(surah_meta.name_string)

        data = zip(hifz_list, surah_meta_list)
        return data

class AyatListView(generic.ListView):
    template_name = 'qurandata/ayatlist.html'
    context_object_name = 'ayat_list_for_surah'

    def get_queryset(self):
        # hifz = get_object_or_404(Hifz, pk=self.kwargs['pk'])
        # return Hifz.objects.filter(surah_number=hifz.surah_number)
        hifz_list = Hifz.objects.filter(surah_number=self.kwargs['surah_number'])
        for hifz in hifz_list:
            hifz.last_refreshed_period_string = hifz.get_last_refreshed_timelength()

        return hifz_list


# def submit(request):
#     if request.method == 'POST':
#         hifzform = HifzForm(request.POST)
#         surah_number = request.POST.get('surah_number')
#         ayat_number = request.POST.get('ayat_number')
#         lower_bound = request.POST.get('min_range')
#         upper_bound = request.POST.get('max_range')
#         ayat_mode = request.POST.get('ayat-mode')
#
#         if hifzform.is_valid():
#             ayat_list = []
#             if ayat_mode == 'ayat_number':
#                 print("Doing ayat number")
#                 ayat_list.append(ayat_number)
#
#             if ayat_mode == 'ayat_limit':
#                 print("Doing ayat limit")
#                 for an in range(lower_bound, upper_bound + 1):
#                     ayat_list.append(an)
#
#             ayat_limit = findMetaSurah(surah_number)
#
#             for an in ayat_list:
#                 if int(an) <= ayat_limit:
#                     save_word_index_difficulty(request, surah_number, an)
#                     message = 'Submission successful'
#                     messages.success(request, message, extra_tags='alert alert-success')
#                 else:
#                     message = "Ayat number {} exceeds limit for surah".format(an)
#                     messages.warning(request, message, extra_tags='alert alert-danger')
#         else:
#             message = "Ayat number exceeds limit for surah"
#             messages.warning(request, message, extra_tags='alert alert-danger')
#
#         return render(request, "qurandata/enter.html")

def enter(request):

    if request.method == 'GET':
        #TODO: need to set limiting on hifz form
        hifzform = HifzForm(request.GET or None)
        if request.GET.get('surah_number') and request.GET.get('ayat_number'):
            data = return_ayat_details(request.GET['surah_number'], request.GET['ayat_number'])

            if data is None:
                messages.warning(request,
                                 "Quran String was not found (due to execeeding ayat)",
                                 extra_tags="alert alert-danger")
                print("Data none")
                return HttpResponseRedirect('')
            else:
                data['hifzform'] = hifzform
                print(data)

                return render(request, 'qurandata/enter.html', data)
        else:
            return render(request, 'qurandata/enter.html', { 'hifzform': hifzform })
    # else:
    #     hifzform = HifzForm(request.GET or None)
    #     return render(request, 'qurandata/enter.html', {'hifzform': hifzform})




    if request.method == 'POST':
        hifzform = HifzForm(request.POST)
        surah_number = request.POST.get('surah_number')
        ayat_number = request.POST.get('ayat_number')
        lower_bound = request.POST.get('min_range')
        upper_bound = request.POST.get('max_range')
        ayat_mode = request.POST.get('ayat-mode')
        default_difficulty = request.POST.get('default_difficulty')
        failed_saving = False

        if hifzform.is_valid():
            ayat_list = []
            if ayat_mode == 'ayat_number':
                ayat_list.append(ayat_number)

            if ayat_mode == 'ayat_limit':
               for an in range(int(lower_bound), int(upper_bound)+ 1):
                    ayat_list.append(an)

            ayat_limit = findMetaSurah(surah_number)

            for an in ayat_list:
                if int(an) <= ayat_limit:
                    dd = 3
                    if default_difficulty:
                        dd = default_difficulty
                    save_word_index_difficulty(request, surah_number, an, dd)
                else:
                    message = "Ayat number {} exceeds limit for surah".format(an)
                    messages.warning(request, message, extra_tags='alert alert-danger')

            if not failed_saving:
                message = 'Submission successful'
                messages.success(request, message, extra_tags='alert alert-success')
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
        print("Returning none")
        return None

    to_display = qm.ayat_string.split(" ")
    form_meta = {}
    display_meta = []
    for i, disp in enumerate(to_display):
        form_meta["class-word-" + str(i)] = "word-" + str(i)
        display_meta.append("class-word-" + str(i))

    hifz_query = Hifz.objects.filter(surah_number=surah_number, ayat_number=ayat_number)

    if hifz_query:
        wordindexset = hifz_query[0].wordindex_set.all()
        tablecolorset = [get_string_table_type_from_difficulty(w.difficulty) for w in wordindexset]
        wordindexsetdifficulties = [w.difficulty for w in wordindexset]
    else:
        tablecolorset = [get_string_table_type_from_difficulty(3) for w in range(0, len(to_display))]
        wordindexsetdifficulties = [3 for w in range(0, len(to_display))]


    display_with_meta = (to_display, display_meta, tablecolorset, wordindexsetdifficulties)

    sm = SurahMeta.objects.filter(surah_number=surah_number)
    sm = sm[0]
    surah_name = sm.name_string

    data = {'display_with_meta': display_with_meta, 'surah_name': surah_name}
    return data

def save_word_index_difficulty(request, surah_number, ayat_number, default_difficulty):
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
        if not wordindex_difficulty:
            wordindex_difficulty = default_difficulty

        if wset:
            w = wset.filter(index=i)
            w = w[0]
            # print("Index {} Old Difficulty {} New Difficulty {}".format(w.index, w.difficulty, wordindex_difficulty))
            w.difficulty = int(wordindex_difficulty)
            w.save()
        else:
            # print("Creating new word indices")
            WordIndex(index=i, difficulty=int(wordindex_difficulty), hifz=hifz).save()


def detail(request, surah_number, ayat_number):
    data = return_ayat_details(surah_number,ayat_number)

    if request.method == 'GET':
        # print(data)
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

