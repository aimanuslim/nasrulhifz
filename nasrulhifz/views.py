from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy

from django.contrib import messages
from django.db import transaction

from .models import Hifz, QuranMeta, WordIndex, SurahMeta, Category
from .serializers import *
from .forms import HifzForm
from numpy import take

from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView

import random
from datetime import date

from .forms import CustomUserCreationForm, ReviseForm

from rest_framework import generics, status, mixins, parsers, permissions, renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.authtoken.models import Token

from os.path import join

import sqlite3

from .permissions import IsOwner
from django.contrib.auth.models import User


class CreateUserView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as E:
            print(E)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    model = User
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = UserSerializer


class SignUp(generic.CreateView):
    # form_class = UserCreationForm
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        messages.success(self.request, "You are registered! Please enter your login details to continue.",
                         extra_tags='alert alert-success custom-size')
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
        surah_number = request.POST.get('surah_number')
        ayat_number_list = request.POST.getlist('ayat_number')
        delete_action = 'delete' in request.POST

        if surah_number:
            surah_number = int(surah_number)
            ayat_number_list = [int(n) for n in ayat_number_list]
            for ayat_number in ayat_number_list:
                h = Hifz.objects.filter(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number)
                if delete_action:
                    h.delete()
                else:
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
class HifzList(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
               generics.GenericAPIView):
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
            serializer = self.get_serializer(instance=objs, data=data, many=True, partial=True)
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

    def patch(self, request, *args, **kwargs):
        data = parsers.JSONParser().parse(request)
        for d in data:
            if d.get('surah_number') == None or d.get('ayat_number') == None:
                return HttpResponseBadRequest("Either ayat number or surah number is missing in body.")
            try:
                hobj = Hifz.objects.get(hafiz=self.request.user, surah_number=d['surah_number'],
                                        ayat_number=d['ayat_number'])
                hobj.delete()
            except:
                raise NotFound('Hifz for deletion does not exist.')

        return HttpResponse("Deletion successfull.")


class HifzDeleteSingle(generics.DestroyAPIView):
    serializer_class = HifzSerializer
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
        surah_number_upperbound = self.request.query_params.get('surah_number_upperbound', None)
        surah_number_lowerbound = self.request.query_params.get('surah_number_lowerbound', None)
        juz_number = self.request.query_params.get('juz_number', None)
        juz_number_upperbound = self.request.query_params.get('juz_number_upperbound', None)
        juz_number_lowerbound = self.request.query_params.get('juz_number_lowerbound', None)
        num_questions = self.request.query_params.get('number_of_questions', 1)
        blind_count = self.request.query_params.get('blind_count', 1)

        try:
            num_questions = int(num_questions)
            blind_count = int(blind_count)

            if surah_number is not None: surah_number = int(surah_number)
            if surah_number_upperbound is not None: surah_number_upperbound = int(surah_number_upperbound)
            if surah_number_lowerbound is not None: surah_number_lowerbound = int(surah_number_lowerbound)
            if juz_number is not None: juz_number = int(juz_number)
            if juz_number_upperbound is not None: juz_number_upperbound = int(juz_number_upperbound)
            if juz_number_lowerbound is not None: juz_number_lowerbound = int(juz_number_lowerbound)
        except:
            content = {'message': 'parameter invalid'}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        if juz_number is not None and surah_number is not None:
            content = {'message': 'cannot have both surah and juz numbers'}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        # free mode
        if juz_number is None and surah_number is None and surah_number_lowerbound is None and surah_number_upperbound is None and juz_number_lowerbound is None and juz_number_lowerbound is None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user).order_by('last_refreshed')
        # juz mode
        elif juz_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, juz_number=juz_number).order_by(
                'last_refreshed')
        # surah mode
        elif surah_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, surah_number=surah_number).order_by(
                'last_refreshed')
        elif surah_number_lowerbound is not None and surah_number_upperbound is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, surah_number__range=(
            surah_number_lowerbound, surah_number_upperbound)).order_by(
                'last_refreshed')
        elif juz_number_lowerbound is not None and juz_number_upperbound is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, juz_number__range=(
            juz_number_lowerbound, juz_number_upperbound)).order_by(
                'last_refreshed')

        # check if hifz_to_revise actually has something
        if len(hifz_to_revise) < 1:
            raise NotFound('Not enough hifz for revision')

        all_hifz_to_revise_indices = range(len(hifz_to_revise))
        if len(hifz_to_revise) >= num_questions:
            k_value = num_questions
        else:
            k_value = len(hifz_to_revise)

        hifz_random_indices = random.sample(all_hifz_to_revise_indices, k_value)

        if len(hifz_to_revise) > 1:
            hifz_to_revise = take(hifz_to_revise, hifz_random_indices)

        all = QuranMeta.objects.all()
        queryset = QuranMeta.objects.none()

        # new blind count logic
        if blind_count % 2 == 0:  # even
            ayat_before = blind_count // 2 - 1
        else:
            ayat_before = blind_count // 2
        ayat_after = blind_count // 2

        list_of_streaks = []
        for i, hifz in enumerate(hifz_to_revise):
            surah_meta = SurahMeta.objects.get(surah_number=hifz.surah_number)
            final_blinded_ayat = hifz.ayat_number + blind_count
            if final_blinded_ayat > surah_meta.surah_ayat_max:
                final_blinded_ayat = surah_meta.surah_ayat_max
            currjson = {"test_index": [i for i in range(hifz.ayat_number, final_blinded_ayat)],
                        "surah_number": surah_meta.surah_number}
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
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, juz_number=juz_number).order_by(
                'last_refreshed')
        # surah mode
        elif surah_number is not None:
            hifz_to_revise = Hifz.objects.filter(hafiz=self.request.user, surah_number=surah_number).order_by(
                'last_refreshed')

        # check if hifz_to_revise actually has something
        if len(hifz_to_revise) < 1:
            raise NotFound('Not enough hifz for revision')

        all_hifz_to_revise_indices = range(len(hifz_to_revise))
        if len(hifz_to_revise) >= streak:
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
            queryset = queryset | all.filter(surah_number=hifz.surah_number, ayat_number__gte=start_ayat_number,
                                             ayat_number__lte=end_ayat_number)
        return queryset


@login_required
def detail(request, surah_number, ayat_number):
    data = return_ayat_details(request, request.user, surah_number, ayat_number)

    if request.method == 'GET':
        # print(data)
        return render(request, 'nasrulhifz/detail.html', data)

    if request.method == 'POST':
        save_word_index_difficulty(request=request, surah_number=surah_number, ayat_number=ayat_number)

        message = "Word difficulties updated."
        messages.success(request, message)
        return HttpResponseRedirect("")

def get_image(request):
    url = get_url_given_surah_number_and_ayat_number(request, request.GET.get('surah_number'), request.GET.get('ayat_number'))
    return JsonResponse({'url': url}) 

@login_required
def enter(request):
    if request.method == 'GET':
        hifzform = HifzForm(request.GET or None)
        categories = Category.objects.all()
        print(categories)
        # print("Check limits {}".format(request.GET.get('change_limits')))
        if request.GET.get('ayat-mode'):
            ayat_mode = request.GET.get('ayat-mode')
            if ayat_mode == 'ayat_number': 
                enter_tag = True
                # ayat_range = True
            else: 
                # ayat_range = True
                enter_tag = False
            
            return render(request, 'nasrulhifz/enter.html', {
                'hifzform': hifzform, 
                'enter_tag': enter_tag,
                'ayat_range': ayat_range
                })
            
        if request.GET.get('change_limits'):
            surah_number = request.GET.get('surah_number')
            surah_limit = findMetaSurah(surah_number)
            # print("Here")
            return JsonResponse({'surah_limit': surah_limit})

        if request.GET.get('surah_number') and request.GET.get('ayat_number'):
            data = return_ayat_details(request, request.user, request.GET['surah_number'], request.GET['ayat_number'])

            if data is None:
                messages.warning(request,
                                 "Quran String was not found (due to execeeding ayat)",
                                 extra_tags="alert alert-danger")
                # print("Data none")
                return HttpResponseRedirect('')
            else:

                data['hifzform'] = hifzform
                data['categories'] = categories

                return render(request, 'nasrulhifz/enter.html', data)
        else:
            return render(request, 'nasrulhifz/enter.html', {'hifzform': hifzform, 'categories': categories})

    if request.method == 'POST':
        hifzform = HifzForm(request.POST)
        surah_number = request.POST.get('surah_number')
        ayat_number = request.POST.get('ayat_number')
        lower_bound = request.POST.get('min_range')
        upper_bound = request.POST.get('max_range')
        ayat_mode = request.POST.get('ayat-mode')
        default_difficulty = request.POST.get('default_difficulty')
        failed_saving = False
        
        # Get the category field from the form data
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')

        # add a new counter
        
        # Create a new category if a name is provided
        if new_category_name:
            category = Category.objects.create(name=new_category_name)
            category_id = category.id

        if hifzform.is_valid():
            ayat_list = []
            for n in range(int(lower_bound), int(upper_bound) + 1):
                ayat_list.append(n)

            ayat_limit = findMetaSurah(surah_number)

            for an in ayat_list:
                dd = 3
                if default_difficulty:
                    dd = default_difficulty
                save_hifz_with_wordindex(request, surah_number, an, dd, category_id)
                # create_hifz_with_wordindex(request, surah_number, an, dd, category_id)

            if not failed_saving:
                message = 'Submission successful'
                messages.success(request, message, extra_tags='alert alert-success')
        else:
            for values in hifzform.errors.values():
                messages.warning(request, values.data[0].message, extra_tags='alert alert-danger')

        return render(request, 'nasrulhifz/enter.html', {'hifzform': hifzform})


def get_url_given_surah_number_and_ayat_number(request, surah_number, ayat_number):
    return 'http://' + request.META['HTTP_HOST'] + "/nasrulhifz/media/images/width_1260/page{:03}.png".format(
        get_page_number_given_ayat_number(surah_number, ayat_number))


def get_page_number_given_ayat_number(surah_number, ayat_number):
    conn = sqlite3.connect(join("data", "ayahinfo_1260.db"))
    res = conn.cursor().execute(
        "SELECT page_number, line_number, position, min_x, max_x, min_y, max_y FROM glyphs WHERE sura_number={} AND ayah_number={};".format(
            surah_number, ayat_number))
    data = res.fetchone()
    page_number = data[0]
    return page_number


def get_page_and_boundaries_given_ayat_and_blind_vicinity(surah_number, ayat_number, vicinity):
    # returns a list of pages with its boundaries, given ayat and its ayat around it
    conn = sqlite3.connect(join("data", "ayahinfo_1260.db"))
    data = dict()

    end_range_ayat_number = ayat_number + vicinity

    # check if the last ayat is beyond the last ayat of surah
    qm = SurahMeta.objects.get(surah_number=surah_number)
    if end_range_ayat_number > qm.surah_ayat_max: end_range_ayat_number = qm.surah_ayat_max

    result = conn.cursor().execute(
        "SELECT page_number, min_x, max_x, min_y, max_y FROM glyphs WHERE sura_number={} AND ayah_number BETWEEN {} AND {};".format(
            surah_number, ayat_number, end_range_ayat_number))
    result = result.fetchall()

    unique_page_numbers = list(set([row[0] for row in result]))
    for pg_number in unique_page_numbers:
        boundaries_for_page = [[row[1], row[2], row[3], row[4]] for row in result if row[0] == pg_number]
        data["page_number"] = pg_number
        data["boundaries"] = boundaries_for_page
    print(data)
    return data


def get_boundaries_given_list_of_ayat_for_surah(page_number, surah_number, ayatlist):
    conn = sqlite3.connect(join("data", "ayahinfo_1260.db"))
    boundary_list = list()
    for ayat_number in ayatlist:
        res = conn.cursor().execute(
            "SELECT page_number, line_number, position, min_x, max_x, min_y, max_y FROM glyphs WHERE page_number={} AND sura_number={} AND ayah_number={};".format(
                page_number, surah_number, ayat_number))
        data = res.fetchall()
        # unique_line_number = set([gdata[1] for gdata in data])
        # print("Ayat number {} Unique line numbers {}".format(ayat_number, unique_line_number))
        # for ln in unique_line_number:
        #     boundary_list.append(get_boundary_given_list_of_glyph_data([gdata for gdata in data if gdata[1] == ln])
        # )

        for glyph_data in data:
            boundary_list.append([
                glyph_data[3],
                glyph_data[4],
                glyph_data[5],
                glyph_data[6],
            ])

    return boundary_list


class ReviseNoUser(APIView):
    def get(self, request):
        mode = self.request.query_params.get('mode', None)
        min_range = self.request.query_params.get('min_range', None)
        max_range = self.request.query_params.get('max_range', None)
        test_count = self.request.query_params.get('test_count', None)
        verse_to_be_hidden = self.request.query_params.get('verse_to_be_hidden', None)

        min_range = int(min_range)
        max_range = int(max_range)
        verse_to_be_hidden = int(verse_to_be_hidden)
        test_count = int(test_count)

        if mode == 'juzMode':
            quran_metas_within_range = list(
                QuranMeta.objects.filter(juz_number__gte=min_range).filter(juz_number__lte=max_range))

        if mode == 'surahMode':
            quran_metas_within_range = list(
                QuranMeta.objects.filter(surah_number__gte=min_range).filter(surah_number__lte=max_range))

        selected_qm = random.sample(quran_metas_within_range, test_count)
        question_data = [
            get_page_and_boundaries_given_ayat_and_blind_vicinity(qm.surah_number, qm.ayat_number, verse_to_be_hidden)
            for qm in selected_qm]

        return Response(question_data)


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
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user, juz_number=unit_number).order_by(
                    'last_refreshed')
            if mode == 'surah_mode':
                unit_number = int(request.POST.get('unit-number'))
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user, surah_number=unit_number).order_by(
                    'last_refreshed')

            if mode == 'free_mode':
                hifz_to_revise = Hifz.objects.filter(hafiz=request.user).order_by('last_refreshed')

            hifz_random_indices = random.sample(
                range(len(hifz_to_revise)) if len(hifz_to_revise) >= streak_length else range(streak_length),
                streak_length)

            if len(hifz_to_revise) > 1:
                hifz_to_revise = take(hifz_to_revise, hifz_random_indices)

            ## new implementation (w2 sept 2020), for each hifz to revise, return its vicinity information
            blind_count = request.POST.get('blind-count')
            blind_count = int(blind_count)

            meta = []
            for hifz in hifz_to_revise:
                url = get_url_given_surah_number_and_ayat_number(request, hifz.surah_number, hifz.ayat_number)
                sm = SurahMeta.objects.filter(surah_number=hifz.surah_number)
                sm = sm[0]
                surah_name = sm.name_string

                page_number = get_page_number_given_ayat_number(hifz.surah_number, hifz.ayat_number)

                blinded_ayats = []
                for i in range(blind_count):
                    blinded_ayats.append(hifz.ayat_number + i + 1)
                    blinded_ayats.append(hifz.ayat_number - i - 1)
                blinded_ayats.append(hifz.ayat_number)

                boundaries_for_current_tested_hifz = get_boundaries_given_list_of_ayat_for_surah(page_number,
                                                                                                 hifz.surah_number,
                                                                                                 blinded_ayats)
                meta.append([
                    url,
                    boundaries_for_current_tested_hifz,
                    surah_name,
                    hifz.surah_number,
                    hifz.ayat_number
                ])
            return render(request, 'nasrulhifz/revise.html', {'meta': meta})
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


def get_boundary_given_list_of_glyph_data(glyph_coord_list):
    minxs = [data[3] for data in glyph_coord_list]
    maxxs = [data[4] for data in glyph_coord_list]
    minys = [data[5] for data in glyph_coord_list]
    maxys = [data[6] for data in glyph_coord_list]

    absminx = min(minxs)
    absminy = min(minys)
    absmaxx = max(maxxs)
    absmaxy = max(maxys)
    return [
        absminx,
        absmaxx,
        absminy,
        absmaxy
    ]


def return_ayat_details(request, user, surah_number, ayat_number):
    conn = sqlite3.connect(join("data", "ayahinfo_1260.db"))
    res = conn.cursor().execute(
        "SELECT page_number, line_number, position, min_x, max_x, min_y, max_y FROM glyphs WHERE sura_number={} AND ayah_number={};".format(
            surah_number, ayat_number))
    data = res.fetchall()

    unique_line_number = set([gdata[1] for gdata in data])
    page_number = data[0][0]

    boundary_list = list()
    for ln in unique_line_number:
        boundary_list.append(get_boundary_given_list_of_glyph_data([gdata for gdata in data if gdata[1] == ln])
                             )

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
            'surah_number': surah_number,
            'image_url': 'http://' + request.META[
                'HTTP_HOST'] + "/nasrulhifz/media/images/width_1260/page{:03}.png".format(page_number),
            'gcoords': boundary_list
            }
    return data


def get_length_of_word_indexes(surah_number, ayat_number):
    conn = sqlite3.connect(join("data", "ayahinfo_1260.db"))
    res = conn.cursor().execute(
        "SELECT position, min_x, max_x, min_y, max_y FROM glyphs WHERE sura_number={} AND ayah_number={};".format(
            surah_number, ayat_number))
    data = res.fetchall()
    return len(data)

@transaction.atomic
def save_hifz_with_wordindex(request, surah_number, ayat_number, default_difficulty, category_id=None):
    # Use get_or_create instead of filter + create
    hifz, _ = Hifz.objects.get_or_create(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number)

    # Update the existing category or create a new one
    if category_id:
        category = Category.objects.filter(id=category_id).first()
        if not category:
            messages.warning(request, f"Invalid category ID: {category_id}", extra_tags='alert alert-danger')
            return
    else:
        new_category_name = request.POST.get('new_category')
        if new_category_name:
            category, _ = Category.objects.get_or_create(name=new_category_name)
        else:
            category = None

    # Update the Hifz and WordIndex objects
    hifz.last_refreshed = date.today()
    hifz.juz_number = QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)[0].juz_number
    hifz.average_difficulty = default_difficulty
    hifz.save()

    wset = WordIndex.objects.filter(hifz=hifz)
    len_wset = get_length_of_word_indexes(surah_number, ayat_number)
    word_indices = []
    for i in range(0, len_wset):
        wordindex_difficulty = request.POST.get("class-word-" + str(i))
        if not wordindex_difficulty:
            wordindex_difficulty = default_difficulty

        try:
            w = wset.get(index=i)
            w.difficulty = int(wordindex_difficulty)
            w.save()
        except WordIndex.DoesNotExist:
            word_indices.append(WordIndex(index=i, difficulty=int(wordindex_difficulty), hifz=hifz))

    WordIndex.objects.bulk_create(word_indices)

    hifz.save_average_difficulty()
    hifz.category = category  # Update the category field
    hifz.save()


@transaction.atomic
def create_hifz_with_wordindex(request, surah_number, ayat_number, default_difficulty, category_id):
    # Get the length/count of WordIndex objects needed
    wordindex_length = get_length_of_word_indexes(surah_number, ayat_number)

    # Create the Hifz object
    hifz = Hifz(hafiz=request.user, surah_number=surah_number, ayat_number=ayat_number, juz_number= QuranMeta.objects.filter(surah_number=surah_number, ayat_number=ayat_number)[0].juz_number,
                  average_difficulty= default_difficulty, category_id=category_id)
    hifz.save()

    # Create the WordIndex objects for the Hifz object
    word_indices = [WordIndex(hifz=hifz, index=i, difficulty=default_difficulty) for i in range(wordindex_length)]
    WordIndex.objects.bulk_create(word_indices)

    return hifz

def create_word_indices(request, wset, len_wset, hifz, default_difficulty):
    word_indices = []
    for i in range(0, len_wset):
        wordindex_difficulty = request.POST.get("class-word-" + str(i))
        if not wordindex_difficulty:
            wordindex_difficulty = default_difficulty

        obj, created = wset.update_or_create(hifz=hifz, index=i, defaults={"difficulty": int(wordindex_difficulty)})
        if created:
            obj.hifz = hifz
            word_indices.append(obj)

    return word_indices

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


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user:
            raise NotFound('User does not exist.')
        token, created = Token.objects.get_or_create(user=user)

        content = {
            'token': token.key,
        }

        return Response(content)
