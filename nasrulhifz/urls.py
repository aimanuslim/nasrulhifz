from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required
app_name = 'nasrulhifz'

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('<int:surah_number>/ayats/', login_required(views.AyatListView.as_view()), name="ayatlist"),
    path('enter/', views.enter, name='enter'),
    path('revise/', views.revise, name='revise'),
    path('<int:surah_number>/ayats/<int:ayat_number>/', views.detail, name="detail"),
    path('api/', views.ProductList.as_view())
]