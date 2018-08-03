from django.urls import path

from . import views

app_name = 'qurandata'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    path('<int:pk>/', views.DetailView.as_view(), name="detail"),
    path('<int:surah_number>/ayats/', views.AyatListView.as_view(), name="ayatlist"),
    path('submit/', views.submit, name='submit')
]