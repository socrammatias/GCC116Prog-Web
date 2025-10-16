from django.contrib import admin
from .models import Materia, Tarefa, Prova, MaterialDeApoio

# 1. Definição do Material Inline (para aparecer dentro da Prova)
class MaterialDeApoioInline(admin.TabularInline):
    # Usa o modelo que será incorporado
    model = MaterialDeApoio 
    # Define campos visíveis no painel
    fields = ['titulo', 'tipo', 'link_url', 'arquivo']
    # Número de formulários extras para novos materiais
    extra = 1 
    # Permite apenas um campo de arquivo ou link preenchido
    # Isso exige validação no admin, mas é opcional para o requisito mínimo.
    # verbose_name_plural = "Materiais de Apoio" 

# 2. Customização da Prova no Admin
@admin.register(Prova)
class ProvaAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de Provas
    list_display = ('titulo', 'materia', 'data_prova', 'tem_material')
    # Filtros na barra lateral
    list_filter = ('materia', 'data_prova')
    # Campos pesquisáveis
    search_fields = ('titulo', 'materia__nome')
    # Inlines para adicionar materiais
    inlines = [MaterialDeApoioInline]

    # Função customizada para verificar se a prova tem material (melhora a lista)
    @admin.display(description='Materiais')
    def tem_material(self, obj):
        return obj.materiais.exists()
    tem_material.boolean = True # Exibe um ícone de check/X

# 3. Customização da Tarefa (se você já tinha, mantenha a importação)
@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'materia', 'data_fim', 'prioridade', 'status')
    list_filter = ('status', 'prioridade', 'materia')
    search_fields = ('titulo', 'descricao')
    list_editable = ('status', 'prioridade') # Permite edição rápida

# 4. Registro simples da Matéria
@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nomenclatura', 'usuario')
    search_fields = ('nome', 'nomenclatura')
    list_filter = ('usuario',)