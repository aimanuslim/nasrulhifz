from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from django.contrib import messages
import random

from .models import Hifz, QuranMeta, WordIndex, SurahMeta
from .forms import HifzForm
from numpy import take

from django.contrib.auth.decorators import login_required
import random
from datetime import date

from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm

class SignUp(generic.CreateView):
    # form_class = UserCreationForm
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'



    def form_valid(self, form):
        messages.success(self.request, "You are registered! Please enter your login details to continue.",extra_tags='alert alert-success custom-size')
        return super().form_valid(form)





class IndexView(generic.ListView):
    template_name = 'qurandata/index.html'
    context_object_name = 'latest_quran_data'

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        hifz_list = Hifz.objects.filter(hafiz=self.request.user).order_by('surah_number').values(
            'surah_number').distinct()
        if len(hifz_list) == 0:
            return None

        surah_meta_list = []
        for hifz in hifz_list:
            surah_meta_list.append(getSurahString(hifz.get('surah_number')))

        data = zip(hifz_list, surah_meta_list)
        return data


class AyatListView(generic.ListView):
    template_name = 'qurandata/ayatlist.html'
    context_object_name = 'ayat_list_for_surah'

    def get_queryset(self):
        # hifz = get_object_or_404(Hifz, pk=self.kwargs['pk'])
        # return Hifz.objects.filter(surah_number=hifz.surah_number)
        hifz_list = Hifz.objects.filter(hafiz=self.request.user, surah_number=self.kwargs['surah_number'])
        for hifz in hifz_list:
            hifz.last_refreshed_period_string = hifz.get_last_refreshed_timelength()
            hifz.days_since_last_refreshed = hifz.get_number_of_days_since_refreshed()
            hifz.average_difficulty = "{0:.2f}".format(hifz.get_hifz_average_difficulty())

        return hifz_list


@login_required
def detail(request, surah_number, ayat_number):
    data = return_ayat_details(request.user, surah_number, ayat_number)

    if request.method == 'GET':
        # print(data)
        return render(request, 'qurandata/detail.html', data)

    if request.method == 'POST':
        save_word_index_difficulty(request=request, surah_number=surah_number, ayat_number=ayat_number)

        message = "Word difficulties updated."
        messages.success(request, message)
        return HttpResponseRedirect("")


@login_required
def enter(request):
    if request.method == 'GET':
        hifzform = HifzForm(request.GET or None)
        # print("Check limits {}".format(request.GET.get('change_limits')))
        if request.GET.get('change_limits'):
            surah_number = request.GET.get('surah_number')
            surah_limit = findMetaSurah(surah_number)
            # print("Here")
            return JsonResponse({'surah_limit': surah_limit})

        if request.GET.get('surah_number') and request.GET.get('ayat_number'):
            data = return_ayat_details(request.user, request.GET['surah_number'], request.GET['ayat_number'])

            if data is None:
                messages.warning(request,
                                 "Quran String was not found (due to execeeding ayat)",
                                 extra_tags="alert alert-danger")
                # print("Data none")
                return HttpResponseRedirect('')
            else:

                data['hifzform'] = hifzform
                # print(data)

                return render(request, 'qurandata/enter.html', data)
        else:
            return render(request, 'qurandata/enter.html', {'hifzform': hifzform})

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
                for an in range(int(lower_bound), int(upper_bound) + 1):
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

@login_required
def revise(request):
    if request.method == 'GET':
        return render(request, "qurandata/revise.html", {'mode_select': "true"})

    if request.method == 'POST':
        # TODO: make it so that we can hide the whole ayat
        if request.POST.get('hifz_was_refreshed') == 'true':
            surah_number = request.POST.get('surah_number')
            ayat_number = request.POST.get('ayat_number')
            # print(ayat_number)
            h = Hifz.objects.filter(hafiz=request.user, surah_number=int(surah_number), ayat_number=int(ayat_number))

            if len(h) > 0:
                h = h[0]
                h.last_refreshed = date.today()
                h.save()
                return render(request, 'qurandata/revise.html')
            else:
                raise Http404()

        if request.POST.get('mode-select') and request.POST.get('streak-length'):
            streak_length = int(request.POST.get('streak-length'))
            mode = request.POST.get('mode-select')
            unit_number= int(request.POST.get('unit-number'))


            if mode == 'juz_mode':
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user, juz_number=unit_number)
            if mode == 'surah_mode':
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user, surah_number=unit_number)

            hifz_random_indices = random.sample(range(len(hifz_to_revise)) if len(hifz_to_revise) >= streak_length else range(streak_length), streak_length)

            if len(hifz_to_revise) > 1:
                hifz_to_revise = take(hifz_to_revise, hifz_random_indices)


            revision_cards = []
            for hifz in hifz_to_revise:

                revision_strings = []
                wordindexes = hifz.wordindex_set.all()

                # set all words to be visible
                show_word = [True for i in range(len(wordindexes))]


                number_of_words_to_be_shown_or_hidden = 7
                # only hide random words in the ayat
                if len(wordindexes) >= number_of_words_to_be_shown_or_hidden:
                    indices = random.sample(range(len(wordindexes)), number_of_words_to_be_shown_or_hidden)
                else:
                    indices = random.sample(range(len(wordindexes)), len(wordindexes))
                # indices = random.sample(range(len(wordindexes)) if len(wordindexes) >= number_of_words_to_be_shown_or_hidden else range(number_of_words_to_be_shown_or_hidden), number_of_words_to_be_shown_or_hidden)

                for i in indices:
                    show_word[i] = decide_show_or_hidden(wordindexes[i].difficulty)


                # find the string for the ayat
                qm = QuranMeta.objects.filter(surah_number=hifz.surah_number, ayat_number=hifz.ayat_number)
                ays = qm[0].ayat_string
                ays = ays.split(" ")
                revision_strings = qm[0].ayat_string.split(" ")


                # get information about the ayat
                hifz_meta = {'surah_number': hifz.surah_number, 'surah_name': getSurahString(hifz.surah_number), 'ayat_number': hifz.ayat_number}


                # get strings and show/hide information for ayat before and after
                ayatBeforeExist, ayatAfterExist = False,False
                if hifz.ayat_number > 1:
                    ayatBeforeExist = True
                    ayatBeforeQM = QuranMeta.objects.filter(surah_number=hifz.surah_number, ayat_number=hifz.ayat_number - 1)
                    ayatBeforeCard = [(string, True) for string in ayatBeforeQM[0].ayat_string.split(" ")]
                    ayatBeforeMeta = {'surah_name': getSurahString(hifz.surah_number), 'ayat_number': hifz.ayat_number - 1}

                if hifz.ayat_number < findMetaSurah(hifz.surah_number):
                    ayatAfterExist = True
                    ayatAfterQM = QuranMeta.objects.filter(surah_number=hifz.surah_number, ayat_number=hifz.ayat_number + 1)
                    ayatAfterCard = [(string, True) for string in ayatAfterQM[0].ayat_string.split(" ")]
                    ayatAfterMeta = {'surah_name': getSurahString(hifz.surah_number),
                                      'ayat_number': hifz.ayat_number + 1}




                # gather data in a card
                revision_card = [(string, shown_status) for string, shown_status in zip(revision_strings, show_word)]
                # print("RC {}".format(revision_card))

                StringMetaSet = []
                if ayatBeforeExist: StringMetaSet.append([ayatBeforeMeta, ayatBeforeCard])
                StringMetaSet.append([hifz_meta, revision_card])
                if ayatAfterExist: StringMetaSet.append([ayatAfterMeta, ayatAfterCard])

                allCardsToDisplay = (hifz_meta, StringMetaSet)

                revision_cards.append(allCardsToDisplay)

            # print(revision_cards)
            return render(request, 'qurandata/revise.html', {'revision_cards': revision_cards})
        return render(request, 'qurandata/revise.html')




def decide_show_or_hidden(difficulty):
    prob = random.uniform(0, 1)

    if difficulty < 4:
        if prob < 0.5:
            return True
        else:
            return False
    else:
        return True




def get_string_table_type_from_difficulty(level):
    if level == 1: return "table-danger"
    if level == 2: return "table-primary"
    if level == 3: return "table-success"


def return_ayat_details(user, surah_number, ayat_number):
    qm = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)
    if len(qm) == 1:
        qm = qm[0]
    else:
        # print("Returning none")
        return None

    to_display = qm.ayat_string.split(" ")
    form_meta = {}
    display_meta = []
    for i, disp in enumerate(to_display):
        form_meta["class-word-" + str(i)] = "word-" + str(i)
        display_meta.append("class-word-" + str(i))

    hifz_query = Hifz.objects.filter(hafiz=user, surah_number=surah_number, ayat_number=ayat_number)

    hifz_exists = None
    if hifz_query:
        wordindexset = hifz_query[0].wordindex_set.all()
        tablecolorset = [get_string_table_type_from_difficulty(w.difficulty) for w in wordindexset]
        wordindexsetdifficulties = [w.difficulty for w in wordindexset]
        hifz_exists = True
    else:
        tablecolorset = [get_string_table_type_from_difficulty(3) for w in range(0, len(to_display))]
        wordindexsetdifficulties = [3 for w in range(0, len(to_display))]
        hifz_exists = None

    display_with_meta = (to_display, display_meta, tablecolorset, wordindexsetdifficulties)

    sm = SurahMeta.objects.filter(surah_number=surah_number)
    sm = sm[0]
    surah_name = sm.name_string

    data = {'display_with_meta': display_with_meta,
            'surah_name': surah_name,
            'hifz_exists': hifz_exists,
            'surah_number' : surah_number
            }
    return data


def save_word_index_difficulty(request, surah_number, ayat_number, default_difficulty=3):
    hifz = Hifz.objects.filter(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number)

    if hifz:
        hifz = hifz[0]
        wset = hifz.wordindex_set.all()
        len_wset = len(wset)
    else:
        juz_number = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)[0].juz_number
        hifz = Hifz(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number, juz_number=juz_number)
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

def getSurahString(surah_number):
    sm = SurahMeta.objects.filter(surah_number=surah_number)
    sm = sm[0]
    return sm.name_string
