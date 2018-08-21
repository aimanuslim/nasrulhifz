from django.urls import path

from . import views

app_name = 'qurandata'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:surah_number>/ayats/', views.AyatListView.as_view(), name="ayatlist"),
    # path('submit/', views.submit, name='submit'),
    path('enter/', views.enter, name='enter'),
    path('<int:surah_number>/ayats/<int:ayat_number>/', views.detail, name="detail")

]