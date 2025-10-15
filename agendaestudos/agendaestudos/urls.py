# Em agendaestudos/urls.py

from django.contrib import admin
from django.urls import path, include # Adicione 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta linha diz: "Qualquer URL que não seja 'admin/'
    # deve ser procurada no arquivo de URLs do app 'agenda'"
    path('', include('agenda.urls')), 
]