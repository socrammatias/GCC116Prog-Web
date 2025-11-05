# --- Bloco de Imports Limpo e Organizado ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Garantindo que apenas modelos existentes sejam importados
from .models import Materia, Tarefa, Prova, MaterialDeApoio 
from django.db.models import Count, Q
from django.core import serializers
# Garantindo que apenas forms existentes sejam importados
from .forms import CustomUserCreationForm, MateriaForm, TarefaForm, ProvaForm, MaterialDeApoioForm, CustomLoginForm,HorarioAulaFormSet
from django.utils import timezone
from django import forms
# import json (REMOVIDO pois não é mais necessário sem a lógica de FullCalendar e notas)

# REMOVIDA: def calcular_media_ponderada(materia):

# --- Views de Autenticação e Dashboard ---

def cadastro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}! Agora você pode fazer o login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'agenda/cadastro.html', {'form': form})

# Em agenda/views.py

@login_required
def dashboard(request):
    from .models import HorarioAula

    # 1. Dados Estatísticos de Tarefas
    user_tasks = Tarefa.objects.filter(materia__usuario=request.user)
    total_tarefas = user_tasks.count()
    tarefas_concluidas = user_tasks.filter(status='C').count()
    porcentagem_concluida = round((tarefas_concluidas / total_tarefas) * 100) if total_tarefas > 0 else 0

    # 1B. Dados Estatísticos de PROVAS
    user_provas = Prova.objects.filter(materia__usuario=request.user)
    total_provas = user_provas.count()
    provas_futuras = user_provas.filter(data_prova__gte=timezone.now().date()).count()

    # 2. Tarefas Urgentes e Próximas
    tarefas_urgentes = user_tasks.filter(status__in=['A', 'E'], prioridade='A').order_by('data_fim')[:5]
    tarefas_proximas = user_tasks.filter(status__in=['A', 'E']).order_by('data_fim')[:5]

    # 2B. Próximas PROVAS
    proximas_provas = user_provas.filter(data_prova__gte=timezone.now().date()).order_by('data_prova')[:5]

    # 3. Distribuição por Matéria
    distribuicao_materias = Materia.objects.filter(usuario=request.user).annotate(
        total_tarefas=Count('tarefas'),
        tarefas_pendentes=Count('tarefas', filter=Q(tarefas__status__in=['A', 'E'])),
        total_provas=Count('provas'),
        total_materiais=Count('provas__materiais')
    ).order_by('-tarefas_pendentes')

    # --- QUADRO DE HORÁRIOS ---
    hoje = timezone.localtime().date()
    hora_atual = timezone.localtime().time()

    dia_semana_num = hoje.weekday()  # 0 = Segunda, 6 = Domingo
    DIAS_MAP = {0: 'SEG', 1: 'TER', 2: 'QUA', 3: 'QUI', 4: 'SEX', 5: 'SAB', 6: 'DOM'}
    dia_semana_sigla = DIAS_MAP.get(dia_semana_num, 'SEG')

    aulas_hoje = HorarioAula.objects.filter(
        materia__usuario=request.user,
        dia_semana=dia_semana_sigla
    ).select_related('materia').order_by('hora_inicio')

    # Próxima aula (ainda não ocorrida)
    proxima_aula = aulas_hoje.filter(hora_inicio__gte=hora_atual).first()

    # Caso não haja nenhuma aula futura, e existam aulas hoje, mostra última aula passada
    if not proxima_aula and aulas_hoje.exists():
        proxima_aula = aulas_hoje.last()

    dia_semana_display = next((d[1] for d in HorarioAula.DIAS_SEMANA if d[0] == dia_semana_sigla), 'Hoje')

    context = {
        'total_tarefas': total_tarefas,
        'tarefas_concluidas': tarefas_concluidas,
        'porcentagem_concluida': porcentagem_concluida,
        'tarefas_urgentes': tarefas_urgentes,
        'tarefas_proximas': tarefas_proximas,
        'total_provas': total_provas,
        'provas_futuras': provas_futuras,
        'proximas_provas': proximas_provas,
        'materias': distribuicao_materias,
        'all_materias': Materia.objects.filter(usuario=request.user).count(),
        'proxima_aula': proxima_aula,
        'aulas_hoje': aulas_hoje,
        'dia_semana_display': dia_semana_display,
        'hoje': hoje,
    }
    return render(request, 'agenda/dashboard.html', context)

@login_required
def agenda(request):
    # A view Agenda também precisa de , mas sem a lógica de Provas/Tarefas combinadas
    tarefas = Tarefa.objects.filter(materia__usuario=request.user)
    provas = Prova.objects.filter(materia__usuario=request.user)
    
    # Combina para serialização
    eventos = list(tarefas) + list(provas)
    eventos_json = serializers.serialize('json', eventos)

    context = {
        'eventos_json': eventos_json,
        'materias': Materia.objects.filter(usuario=request.user),
    }
    return render(request, 'agenda/agenda.html', context)


# --- Views de Matérias (Lógica Limpa) ---

@login_required
def materia_list(request):
    materias = Materia.objects.filter(usuario=request.user).annotate(
        total_tarefas=Count('tarefas'),
        tarefas_concluidas=Count('tarefas', filter=Q(tarefas__status='C')),
        total_provas=Count('provas'),
        total_materiais=Count('provas__materiais') 
    ).order_by('nome')

    for materia in materias:
        if materia.total_tarefas > 0:
            porcentagem = (materia.tarefas_concluidas / materia.total_tarefas) * 100
            materia.percentual_concluido = round(porcentagem)
        else:
            materia.percentual_concluido = 0
            
    return render(request, 'agenda/materia_list.html', {'materias': materias})

@login_required
def material_create(request, prova_pk):
    prova = get_object_or_404(Prova, pk=prova_pk, materia__usuario=request.user)
    
    if request.method == 'POST':
        form = MaterialDeApoioForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.prova = prova
            material.tipo = 'LINK'  # força o tipo como LINK
            material.save()
            messages.success(request, 'Material de apoio adicionado com sucesso!')
            return redirect('material_list', prova_pk=prova.pk)
    else:
        form = MaterialDeApoioForm()
    
    context = {
        'form': form,
        'prova': prova,
        'title': f'Adicionar Material para {prova.titulo}'
    }
    return render(request, 'agenda/material_form.html', context)


@login_required
def materia_create(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            materia = form.save(commit=False)
            materia.usuario = request.user
            materia.save()
            messages.success(request, 'Matéria criada com sucesso!')
            return redirect('materia_list')
    else:
        form = MateriaForm()
    return render(request, 'agenda/materia_form.html', {'form': form, 'title': 'Nova Matéria', 'is_notes_view': False})

@login_required
def materia_update(request, pk):
    materia = get_object_or_404(Materia, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        formset_horarios = HorarioAulaFormSet(request.POST, instance=materia, prefix='horarioaula_set')

        if form.is_valid() and formset_horarios.is_valid():
            form.save()
            formset_horarios.save()
            messages.success(request, "Matéria atualizada com sucesso!")
            return redirect('materia_list')
    else:
        form = MateriaForm(instance=materia)
        formset_horarios = HorarioAulaFormSet(instance=materia, prefix='horarioaula_set')

    context = {
        'form': form,
        'formset_horarios': formset_horarios,
        'materia': materia,
        'title': "Editar Matéria",
    }
    return render(request, 'agenda/materia_form.html', context)

@login_required
def materia_notes_update(request, pk):
    materia = get_object_or_404(Materia, pk=pk, usuario=request.user)
    
    class NotesForm(forms.ModelForm):
        class Meta:
            model = Materia
            fields = ['notas_materia']
            widgets = {
                'notas_materia': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Professor, ementa, requisitos de aprovação, etc.'}),
            }
            labels = {
                'notas_materia': 'Suas Anotações da Matéria',
            }

    if request.method == 'POST':
        form = NotesForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, f'Anotações de {materia.nome} salvas com sucesso!')
            return redirect('materia_list') 
    else:
        form = NotesForm(instance=materia)
        
    context = {
        'form': form,
        'title': f'Editar Anotações: {materia.nome}',
        'materia': materia,
        'is_notes_view': True 
    }
    return render(request, 'agenda/materia_form.html', context)

@login_required
def materia_delete(request, pk):
    materia = get_object_or_404(Materia, pk=pk, usuario=request.user)
    if request.method == 'POST':
        materia.delete()
        messages.success(request, 'Matéria deletada com sucesso!')
        return redirect('materia_list')
    return render(request, 'agenda/materia_confirm_delete.html', {'materia': materia})

# --- Views de Tarefas e Provas (Restante) ---
@login_required
def tarefa_concluir(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, materia__usuario=request.user)
    if tarefa.status != 'C':
        tarefa.status = 'C'
        tarefa.save()
        messages.success(request, f'Tarefa "{tarefa.titulo}" marcada como CONCLUÍDA! Bom trabalho!')
    else:
        messages.info(request, f'Tarefa "{tarefa.titulo}" já estava concluída.')
    return redirect('tarefa_list')

@login_required
def tarefa_foco(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, materia__usuario=request.user)
    if tarefa.status == 'C':
        messages.info(request, 'Esta tarefa já está concluída!')
        return redirect('tarefa_list')
    context = {
        'tarefa': tarefa,
        'title': f'Foco: {tarefa.titulo}',
    }
    return render(request, 'agenda/tarefa_foco.html', context)

@login_required
def tarefa_list(request):
    # ... (código existente) ...
    tarefas = Tarefa.objects.filter(materia__usuario=request.user)
    materia_id = request.GET.get('materia')
    status = request.GET.get('status')
    prioridade = request.GET.get('prioridade')
    if materia_id:
        tarefas = tarefas.filter(materia__id=materia_id)
    if status:
        tarefas = tarefas.filter(status=status)
    if prioridade:
        tarefas = tarefas.filter(prioridade=prioridade)
    tarefas = tarefas.order_by('data_inicio')

    context = {
        'tarefas': tarefas,
        'all_materias': Materia.objects.filter(usuario=request.user), 
        'status_choices': Tarefa.STATUS_CHOICES,
        'prioridade_choices': Tarefa.PRIORIDADE_CHOICES,
        'current_filters': {
            'materia': int(materia_id) if materia_id else None,
            'status': status,
            'prioridade': prioridade,
        }
    }
    return render(request, 'agenda/tarefa_list.html', context)

@login_required
def tarefa_create(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa criada com sucesso!')
            return redirect('tarefa_list')
    else:
        form = TarefaForm(user=request.user)
    return render(request, 'agenda/tarefa_form.html', {'form': form, 'title': 'Nova Tarefa'})

@login_required
def tarefa_update(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, materia__usuario=request.user)
    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa atualizada com sucesso!')
            return redirect('tarefa_list')
    else:
        form = TarefaForm(instance=tarefa, user=request.user)
    return render(request, 'agenda/tarefa_form.html', {'form': form, 'title': 'Editar Tarefa'})

@login_required
def tarefa_delete(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk, materia__usuario=request.user)
    if request.method == 'POST':
        tarefa.delete()
        messages.success(request, 'Tarefa deletada com sucesso!')
        return redirect('tarefa_list')
    return render(request, 'agenda/tarefa_confirm_delete.html', {'tarefa': tarefa})


@login_required
def prova_list(request):
    provas = Prova.objects.filter(materia__usuario=request.user).order_by('data_prova')
    materia_id = request.GET.get('materia')
    if materia_id:
        provas = provas.filter(materia__id=materia_id)

    context = {
        'provas': provas,
        'all_materias': Materia.objects.filter(usuario=request.user),
        'current_materia': int(materia_id) if materia_id else None
    }
    return render(request, 'agenda/prova_list.html', context)

@login_required
def prova_create(request):
    if request.method == 'POST':
        form = ProvaForm(request.POST, user=request.user)
        if form.is_valid():
            prova = form.save()
            messages.success(request, 'Prova agendada com sucesso! Adicione os materiais de apoio a seguir.')
            return redirect('material_list', prova_pk=prova.pk) 
    else:
        form = ProvaForm(user=request.user)
    context = {
        'form': form, 
        'title': 'Agendar Nova Prova'
    }
    return render(request, 'agenda/prova_form.html', context)

@login_required
def prova_update(request, pk):
    prova = get_object_or_404(Prova, pk=pk, materia__usuario=request.user)
    if request.method == 'POST':
        form = ProvaForm(request.POST, instance=prova, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prova atualizada com sucesso!')
            return redirect('prova_list')
    else:
        form = ProvaForm(instance=prova, user=request.user)
    context = {
        'form': form, 
        'title': 'Editar Prova',
        'prova': prova 
    }
    return render(request, 'agenda/prova_form.html', context)

@login_required
def prova_delete(request, pk):
    prova = get_object_or_404(Prova, pk=pk, materia__usuario=request.user)
    if request.method == 'POST':
        prova.delete()
        messages.success(request, 'Prova deletada com sucesso!')
        return redirect('prova_list')
    return render(request, 'agenda/prova_confirm_delete.html', {'prova': prova})


@login_required
def material_list(request, prova_pk):
    prova = get_object_or_404(Prova, pk=prova_pk, materia__usuario=request.user)
    materiais = MaterialDeApoio.objects.filter(prova=prova)

    context = {
        'prova': prova,
        'materiais': materiais
    }
    return render(request, 'agenda/material_list.html', context)

@login_required
def materia_create(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        formset_horarios = HorarioAulaFormSet(request.POST, prefix='horarioaula_set')

        if form.is_valid() and formset_horarios.is_valid():
            materia = form.save(commit=False)
            materia.usuario = request.user
            materia.save()

            # associa o formset à matéria criada
            formset_horarios.instance = materia
            formset_horarios.save()

            messages.success(request, "Matéria criada com sucesso!")
            return redirect('materia_list')
    else:
        form = MateriaForm()
        formset_horarios = HorarioAulaFormSet(prefix='horarioaula_set')

    context = {
        'form': form,
        'formset_horarios': formset_horarios,
        'title': "Adicionar Matéria",
    }
    return render(request, 'agenda/materia_form.html', context)

@login_required
def material_delete(request, pk):
    material = get_object_or_404(MaterialDeApoio, pk=pk, prova__materia__usuario=request.user)
    if request.method == 'POST':
        prova_pk = material.prova.pk
        material.delete()
        messages.success(request, 'Material de apoio removido.')
        return redirect('material_list', prova_pk=prova_pk)
    return render(request, 'agenda/material_confirm_delete.html', {'material': material})