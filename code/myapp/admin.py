
# core/admin.py
from django.contrib import admin
from .models import Materia, Tarefa

# Registra os modelos para que apareçam na interface de administração
admin.site.register(Materia)
admin.site.register(Tarefa)