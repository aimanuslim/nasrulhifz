from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponseNotFound, HttpResponse
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from django.contrib import messages


from .models import Hifz, QuranMeta, WordIndex, SurahMeta
from .serializers import *
from .forms import HifzForm
from numpy import take

from django.contrib.auth.decorators import login_required

import random
from datetime import date

from .forms import CustomUserCreationForm, ReviseForm

from rest_framework import generics, status, mixins, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


from .permissions import IsOwner

class SignUp(generic.CreateView):
    # form_class = UserCreationForm
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'



    def form_valid(self, form):
        messages.success(self.request, "You are registered! Please enter your login details to continue.",extra_tags='alert alert-success custom-size')
        return super().form_valid(form)


class IndexView(generic.ListView):
    template_name = 'nasrulhifz/index.html'
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
        # print(hifz_list)
        return data


class AyatListView(generic.ListView):
    template_name = 'nasrulhifz/ayatlist.html'
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

    def post(self, request, *args, **kwargs):
        surah_number = request.POST.get('surah_number')[0]
        ayat_number_list = request.POST.getlist('ayat_number')

        if surah_number:
            surah_number = int(surah_number)
            ayat_number_list = [int(n) for n in ayat_number_list]
            for ayat_number in ayat_number_list:
                h = Hifz.objects.filter(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number)
                h = h[0]
                h.last_refreshed = date.today()
                h.save()

            hifz_list = Hifz.objects.filter(hafiz=request.user, surah_number=surah_number)

            for hifz in hifz_list:
                hifz.last_refreshed_period_string = hifz.get_last_refreshed_timelength()
                hifz.days_since_last_refreshed = hifz.get_number_of_days_since_refreshed()
                hifz.average_difficulty = "{0:.2f}".format(hifz.get_hifz_average_difficulty())

            return render(request, 'nasrulhifz/ayatlist.html', {self.context_object_name: hifz_list})
        else:
            return Http404()

# API for creating, updating, saving new hifzs
class HifzList(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = HifzSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        surah_number = self.request.query_params.get('surah_number', None)
        juz_number = self.request.query_params.get('juz_number', None)
        ayat_number = self.request.query_params.get('ayat_number', None)
        if surah_number is not None and ayat_number is not None:
            return Hifz.objects.filter(hafiz=self.request.user, surah_number=surah_number, ayat_number=ayat_number)
        if surah_number is not None:
            return Hifz.objects.filter(hafiz=self.request.user, surah_number=surah_number)
        if juz_number is not None:
            return Hifz.objects.filter(hafiz=self.request.user, juz_number=juz_number)

        return Hifz.objects.filter(hafiz=self.request.user)


    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = parsers.JSONParser().parse(request)
        if isinstance(data, list):
            serializer = self.get_serializer(data=data, many=True)
        else:
            serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(hafiz=request.user)
            return JsonResponse(serializer.data, safe=False, status=201)
        else:
            return JsonResponse(serializer.errors, safe=False, status=400)

    def patch(self, request, *args, **kwargs):
        data = parsers.JSONParser().parse(request)
        if isinstance(data, list):
            objs = Hifz.objects.filter(hafiz=self.request.user)
            for d in data:
                d['hafiz'] = {'username': self.request.user.username}
            serializer = self.get_serializer(instance=objs, data=data, many=True)
        else:
            try:
                obj = Hifz.objects.get(hafiz=self.request.user,
                                       surah_number=data.get('surah_number'),
                                       ayat_number=data.get('ayat_number'))
                serializer = self.get_serializer(instance=obj, data=data)
            except:
                raise NotFound('Hifz to be updated does not exist.')
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False, status=201)
        else:
            return JsonResponse(serializer.errors, safe=False, status=400)
    


class HifzDeleteMultiple(generics.GenericAPIView, mixins.DestroyModelMixin):
    serializer_class = HifzSerializer
    permission_classes = (IsOwner,)

    def delete(self, request, *args, **kwargs):
        data = parsers.JSONParser().parse(request)
        for d in data:
            if d.get('surah_number') == None or d.get('ayat_number') == None:
                return HttpResponseBadRequest("Either ayat number or surah number is missing in body.")
            try:
                hobj = Hifz.objects.get(hafiz=self.request.user, surah_number=d['surah_number'], ayat_number=d['ayat_number'])
                hobj.delete()
            except:
                raise NotFound('Hifz for deletion does not exist.')
        
        return HttpResponse("Deletion successfull.")





class HifzDeleteSingle(generics.DestroyAPIView):
    serializer_class =  HifzSerializer
    model = Hifz
    permission_classes = (IsOwner,)


    def get_object(self):
        surah_number = self.kwargs.get('surah_number')
        ayat_number = self.kwargs.get('ayat_number')
        try:
            return Hifz.objects.get(hafiz=self.request.user,
                                surah_number=surah_number,
                                ayat_number=ayat_number)
        except:
            raise NotFound('Hifz for deletion does not exist.')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        surah_number = instance.surah_number
        ayat_number = instance.ayat_number
        self.perform_destroy(instance)
        return HttpResponse('Deletion surah number: {}  ayat: {} succeeded'.format(surah_number, ayat_number))



class QuranMetaList(generics.ListAPIView):
    serializer_class = QuranMetaSerializer
    queryset = QuranMeta.objects.all()
    def get_queryset(self):
        queryset = QuranMeta.objects.all()
        surah_number = self.request.query_params.get('surah_number', None)
        juz_number = self.request.query_params.get('juz_number', None)
        if surah_number is not None:
            queryset = queryset.filter(surah_number=surah_number)
            return queryset
        elif juz_number is not None:
            queryset = queryset.filter(juz_number=juz_number)
            return queryset
        else:
            return None


class QuranMetaDetail(generics.RetrieveAPIView):
    serializer_class = QuranMetaSerializer
    model = QuranMeta

    def get_object(self):
        # this how we fetch the parameter from the url format, specified in url.py
        surah_number = self.kwargs.get('surah_number')
        ayat_number = self.kwargs.get('ayat_number')

        return QuranMeta.objects.get(surah_number=surah_number, ayat_number=ayat_number)



class SurahMetaDetail(generics.RetrieveAPIView):
    serializer_class = SurahMetaSerializer
    def get_object(self):
        surah_number = self.kwargs.get('surah_number')
        return SurahMeta.objects.get(surah_number=surah_number)

class ReviseCustomView(APIView):
    def get(self, request):
        surah_number = self.request.query_params.get('surah_number', None)
        juz_number = self.request.query_params.get('juz_number', None)
        vicinity = self.request.query_params.get('vicinity', 1)
        streak = self.request.query_params.get('streak_length', 1)
        blind_count = self.request.query_params.get('blind_count', 1)

        try:
            vicinity = int(vicinity)
            streak = int(streak)
            blind_count = int(blind_count)

            if surah_number is not None: surah_number = int(surah_number)
            if juz_number is not None: juz_number = int(juz_number)
        except:
            content = {'message': 'parameter invalid'}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        if juz_number is not None and surah_number is not None:
            content = {'message': 'cannot have both surah and juz numbers'}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        # free mode
        if juz_number is None and surah_number is None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user).order_by('last_refreshed')
        # juz mode
        elif juz_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, juz_number=juz_number).order_by('last_refreshed')
        # surah mode
        elif surah_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, surah_number=surah_number).order_by(
                'last_refreshed')

        # check if hifz_to_revise actually has something
        if len(hifz_to_revise) < 1:
            raise NotFound('Not enough hifz for revision')


        all_hifz_to_revise_indices = range(len(hifz_to_revise))
        if len(hifz_to_revise)  >= streak:
            k_value = streak
        else:
            k_value = len(hifz_to_revise)


        hifz_random_indices = random.sample(all_hifz_to_revise_indices, k_value)

        if len(hifz_to_revise) > 1:
            hifz_to_revise = take(hifz_to_revise, hifz_random_indices)

        all = QuranMeta.objects.all()
        queryset = QuranMeta.objects.none()

        list_of_streaks = []
        for i, hifz in enumerate(hifz_to_revise):
            surah_meta = SurahMeta.objects.get(surah_number=hifz.surah_number)
            central_ayat_number = hifz.ayat_number
            start_ayat_number = central_ayat_number - blind_count - vicinity
            end_ayat_number = central_ayat_number + blind_count + vicinity
            start_blind_ayat_number = central_ayat_number - blind_count
            end_blind_ayat_number = central_ayat_number + blind_count
            if start_ayat_number < 1: start_ayat_number = 1
            if end_ayat_number > surah_meta.surah_ayat_max: end_ayat_number = surah_meta.surah_ayat_max
            currset = QuranMeta.objects.filter(surah_number=hifz.surah_number, ayat_number__gte=start_ayat_number, ayat_number__lte=end_ayat_number)  
            currsr = QuranMetaSerializer(currset, many=True)   
            currjson = {"test_index": [i for i in range(start_blind_ayat_number, end_blind_ayat_number + 1)], "data": currsr.data}
            list_of_streaks.append(currjson)
        
        return Response(list_of_streaks)


class ReviseList(generics.ListAPIView):
    serializer_class = QuranMetaSerializer
    # serializer_class = QuranMetaListSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        surah_number = self.request.query_params.get('surah_number', None)
        juz_number = self.request.query_params.get('juz_number', None)
        vicinity = self.request.query_params.get('vicinity', 1)
        streak = self.request.query_params.get('streak_length', 1)
        blind_count = self.request.query_params.get('blind_count', 1)

        try:
            vicinity = int(vicinity)
            streak = int(streak)
            blind_count = int(blind_count)

            if surah_number is not None: surah_number = int(surah_number)
            if juz_number is not None: juz_number = int(juz_number)
        except:
            content = {'message': 'parameter invalid'}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        if juz_number is not None and surah_number is not None:
            content = {'message': 'cannot have both surah and juz numbers'}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        # free mode
        if juz_number is None and surah_number is None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user).order_by('last_refreshed')
        # juz mode
        elif juz_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, juz_number=juz_number).order_by('last_refreshed')
        # surah mode
        elif surah_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, surah_number=surah_number).order_by(
                'last_refreshed')

        # check if hifz_to_revise actually has something
        if len(hifz_to_revise) < 1:
            raise NotFound('Not enough hifz for revision')


        all_hifz_to_revise_indices = range(len(hifz_to_revise))
        if len(hifz_to_revise)  >= streak:
            k_value = streak
        else:
            k_value = len(hifz_to_revise)


        hifz_random_indices = random.sample(all_hifz_to_revise_indices, k_value)

        if len(hifz_to_revise) > 1:
            hifz_to_revise = take(hifz_to_revise, hifz_random_indices)

        all = QuranMeta.objects.all()
        queryset = QuranMeta.objects.none()

        for hifz in hifz_to_revise:
            surah_meta = SurahMeta.objects.get(surah_number=hifz.surah_number)
            central_ayat_number = hifz.ayat_number
            start_ayat_number = central_ayat_number - blind_count - vicinity
            end_ayat_number = central_ayat_number + blind_count + vicinity
            if start_ayat_number < 1: start_ayat_number = 1
            if end_ayat_number > surah_meta.surah_ayat_max: end_ayat_number = surah_meta.surah_ayat_max
            queryset = queryset | all.filter(surah_number=hifz.surah_number, ayat_number__gte=start_ayat_number, ayat_number__lte=end_ayat_number)
        return queryset


@login_required
def detail(request, surah_number, ayat_number):
    data = return_ayat_details(request.user, surah_number, ayat_number)

    if request.method == 'GET':
        # print(data)
        return render(request, 'nasrulhifz/detail.html', data)

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

                return render(request, 'nasrulhifz/enter.html', data)
        else:
            return render(request, 'nasrulhifz/enter.html', {'hifzform': hifzform})

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

        return render(request, 'nasrulhifz/enter.html', {'hifzform': hifzform})

@login_required
def revise(request):
    if request.method == 'GET':
        return render(request, "nasrulhifz/revise.html", {'mode_select': "true", 'revise_forms': ReviseForm})

    if request.method == 'POST':
        if request.POST.get('hifz_was_refreshed') == 'true':
            surah_number = request.POST.get('surah_number')
            ayat_number = request.POST.getlist('ayat_number[]')
            for an in ayat_number:
                try:
                    h = Hifz.objects.get(hafiz=request.user, surah_number=int(surah_number), ayat_number=int(an))
                    h.save()
                except:
                    raise Http404('Some hifz does not exist.')

            return render(request, 'nasrulhifz/revise.html')


        if request.POST.get('mode-select') and request.POST.get('streak-length'):
            streak_length = int(request.POST.get('streak-length'))
            mode = request.POST.get('mode-select')



            if mode == 'juz_mode':
                unit_number = int(request.POST.get('unit-number'))
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user, juz_number=unit_number).order_by('last_refreshed')
            if mode == 'surah_mode':
                unit_number = int(request.POST.get('unit-number'))
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user, surah_number=unit_number).order_by('last_refreshed')

            if mode == 'free_mode':
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user).order_by('last_refreshed')





            hifz_random_indices = random.sample(range(len(hifz_to_revise)) if len(hifz_to_revise) >= streak_length else range(streak_length), streak_length)

            if len(hifz_to_revise) > 1:
                hifz_to_revise = take(hifz_to_revise, hifz_random_indices)


            revision_cards = []
            for hifz in hifz_to_revise:

                revision_strings = []
                wordindexes = hifz.wordindex_set.all()

                # set all words to be invisible
                # show_word = [True if (i > 1 and i < len(wordindexes) - 2) else 'Clue' for i in range(len(wordindexes))]
                show_word = [False if (i > 1 and i < len(wordindexes) - 2) else 'Clue' for i in range(len(wordindexes))]


                number_of_words_to_be_shown_or_hidden = 7
                # only hide random words in the ayat
                if len(wordindexes) >= number_of_words_to_be_shown_or_hidden:
                    indices = random.sample(range(len(wordindexes)), number_of_words_to_be_shown_or_hidden)
                else:
                    indices = random.sample(range(len(wordindexes)), len(wordindexes))
                # indices = random.sample(range(len(wordindexes)) if len(wordindexes) >= number_of_words_to_be_shown_or_hidden else range(number_of_words_to_be_shown_or_hidden), number_of_words_to_be_shown_or_hidden)

                # for i in indices:
                #     if (i > 1 and i < len(wordindexes) - 2):
                #         show_word[i] = decide_show_or_hidden(wordindexes[i].difficulty)




                context_count = request.POST.get('context-count')
                context_count = int(context_count)

                StringMetaSet = []

                proximity_tested_ayat = request.POST.get('proximity-count')
                proximity_tested_ayat = int(proximity_tested_ayat)
                upper_limit = findMetaSurah(hifz.surah_number)


                current_ayat_before_number = hifz.ayat_number - context_count - proximity_tested_ayat
                for i in range(context_count):
                    if current_ayat_before_number < (hifz.ayat_number - proximity_tested_ayat) and current_ayat_before_number > 0:
                        ayatBeforeQM = QuranMeta.objects.filter(surah_number=hifz.surah_number,
                                                                ayat_number=current_ayat_before_number)
                        ayatBeforeCard = [(string, True) for string in ayatBeforeQM[0].ayat_string.split(" ")]
                        ayatBeforeMeta = {'surah_name': getSurahString(hifz.surah_number),
                                          'ayat_number': current_ayat_before_number}
                        # print("Before ayat number: " + str(current_ayat_before_number))
                        StringMetaSet.append([ayatBeforeMeta, ayatBeforeCard])
                    current_ayat_before_number += 1

                hifz_meta = {'surah_number': hifz.surah_number, 'surah_name': getSurahString(hifz.surah_number),
                             'ayat_number': hifz.ayat_number}

                proximity_ayat_number = hifz.ayat_number - proximity_tested_ayat

                for i in range(proximity_tested_ayat * 2 + 1):
                    if proximity_ayat_number > 0 and proximity_ayat_number <= upper_limit:
                        # print("Number i: {} prox: {} upper: {}".format(i, proximity_ayat_number, upper_limit))
                        try:
                            
                            h = Hifz.objects.get(hafiz=request.user, surah_number=hifz.surah_number, ayat_number=proximity_ayat_number)
                            # h= h[0] # TODO: fix error with out of index. maybe need to pull from quranmeta instead of from hifz if the hifz doesnt exist when looking around the ayat that is currently being tested.
                            wordindexes = h.wordindex_set.all()

                            show_word = [False if (i > 1 and i < len(wordindexes) - 2) else 'Clue' for i in
                                        range(len(wordindexes))]
                            print("Got here")
                        except: 
                            show_word = None
                        qm = QuranMeta.objects.filter(surah_number=hifz.surah_number, ayat_number=proximity_ayat_number)
                        ays = qm[0].ayat_string
                        ays = ays.split(" ")
                        revision_strings = qm[0].ayat_string.split(" ")

                        if show_word is None: show_word = [False if (i > 1 and i < len(ays) - 2) else 'Clue'  for i, a in enumerate(ays)]

                        print(show_word)
                        # get information about the ayat
                        temp_hifz_meta = {'surah_number': hifz.surah_number, 'surah_name': getSurahString(hifz.surah_number),
                                     'ayat_number': proximity_ayat_number}
                        # print("Proximity ayat number: " + str(proximity_ayat_number))

                        revision_card = [(string, shown_status) for string, shown_status in
                                         zip(revision_strings, show_word)]
                        StringMetaSet.append([temp_hifz_meta, revision_card])
                    proximity_ayat_number += 1


                current_ayat_after_number = hifz.ayat_number + proximity_tested_ayat + 1
                for i in range(context_count):
                    if current_ayat_after_number <= (hifz.ayat_number + proximity_tested_ayat + context_count) and current_ayat_after_number <= upper_limit:
                        ayatAfterQM = QuranMeta.objects.filter(surah_number=hifz.surah_number,
                                                               ayat_number=current_ayat_after_number)
                        ayatAfterCard = [(string, True) for string in ayatAfterQM[0].ayat_string.split(" ")]
                        ayatAfterMeta = {'surah_name': getSurahString(hifz.surah_number),
                                         'ayat_number': current_ayat_after_number}
                        # print("After ayat number: " + str(current_ayat_after_number))
                        StringMetaSet.append([ayatAfterMeta, ayatAfterCard])
                    current_ayat_after_number += 1


                # print(StringMetaSet)
                hifz_meta['ayat_number'] = hifz.ayat_number
                allCardsToDisplay = (hifz_meta, StringMetaSet)



                revision_cards.append(allCardsToDisplay)

            # print(revision_cards)

            return render(request, 'nasrulhifz/revise.html', {'revision_cards': revision_cards})
        return render(request, 'nasrulhifz/revise.html')




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
        hifz.last_refreshed = date.today()
        wset = hifz.wordindex_set.all()
        len_wset = len(wset)
    else:
        juz_number = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)[0].juz_number
        hifz = Hifz(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number, juz_number=juz_number)
        hifz.average_difficulty = default_difficulty
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

    hifz.save_average_difficulty()
    hifz.save()


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
