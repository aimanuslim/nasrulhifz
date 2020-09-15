from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings

app_name = 'nasrulhifz'

urlpatterns = [
    # Web app related URI
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:surah_number>/ayats/', login_required(views.AyatListView.as_view()), name="ayatlist"),
    path('enter/', views.enter, name='enter'),
    path('revise/', views.revise, name='revise'),
    path('<int:surah_number>/ayats/<int:ayat_number>/', views.detail, name="detail"),

    # API related uri
    path('api/', views.HifzList.as_view()),
    path('api/delete/<int:surah_number>/<int:ayat_number>/', views.HifzDeleteSingle.as_view()),
    path('api/delete/', views.HifzDeleteMultiple.as_view()),
    path('api/quranmeta/list/', views.QuranMetaList.as_view()),
    path('api/quranmeta/<int:surah_number>/<int:ayat_number>/', views.QuranMetaDetail.as_view()),
    path('api/surahmeta/<int:surah_number>/', views.SurahMetaDetail.as_view()),
    # path('api/revise/', views.ReviseList.as_view()),
    path('api/revise/', views.ReviseCustomView.as_view()),


    # Authentication for API
    path('api-token-auth/', views.ObtainAuthToken.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('api/register/', views.CreateUserView.as_view()),

    # password reset api
    # path('api/password_reset/', include('django_rest_passwordreset.urls'), name='password_reset'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.DATA_URL, document_root=settings.DATA_ROOT)