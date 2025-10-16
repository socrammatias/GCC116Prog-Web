# Em agendaestudos/urls.py

from django.contrib import admin
from django.urls import path, include # Adicione 'include'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta linha diz: "Qualquer URL que não seja 'admin/'
    # deve ser procurada no arquivo de URLs do app 'agenda'"
    path('', include('agenda.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)