from django.contrib import admin
from .models import Materia, Tarefa # Apenas IMPORTA os modelos do arquivo models.py

# Apenas REGISTRA os modelos no site de administração
admin.site.register(Materia)
admin.site.register(Tarefa)