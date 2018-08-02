from django.urls import path

from . import views

app_name = 'qurandata'

urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:hifz_id>/', views.detail, name="detail")
]