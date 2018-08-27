from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required
app_name = 'qurandata'

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:surah_number>/ayats/', login_required(views.AyatListView.as_view()), name="ayatlist"),
    # path('submit/', views.submit, name='submit'),
    path('enter/', views.enter, name='enter'),
    path('revise/', views.revise, name='revise'),
    path('<int:surah_number>/ayats/<int:ayat_number>/', views.detail, name="detail")
]