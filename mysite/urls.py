from django.contrib import admin
from django.urls import include, path

from nasrulhifz.views import SignUp
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('nasrulhifz/', include('nasrulhifz.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUp.as_view(), name='signup'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)