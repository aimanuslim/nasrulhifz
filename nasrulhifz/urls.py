from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.views import obtain_auth_token
app_name = 'nasrulhifz'

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:surah_number>/ayats/', login_required(views.AyatListView.as_view()), name="ayatlist"),
    path('enter/', views.enter, name='enter'),
    path('revise/', views.revise, name='revise'),
    path('<int:surah_number>/ayats/<int:ayat_number>/', views.detail, name="detail"),
    path('api/', views.HifzList.as_view()),
    path('api-token-auth/', obtain_auth_token)
]