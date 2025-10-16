# Este é o conteúdo COMPLETO e CORRETO para agenda/views.py

# --- Bloco de Imports Limpo e Organizado ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Materia, Tarefa, Prova, MaterialDeApoio
from django.db.models import Count, Q
from django.core import serializers
from .forms import CustomUserCreationForm, MateriaForm, TarefaForm, ProvaForm, MaterialDeApoioForm
from django.utils import timezone

# --- Views de Autenticação e Home (Já existentes) ---

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

@login_required
def dashboard(request):
    # 1. Dados Estatísticos de Tarefas
    # Filtra todas as tarefas que pertencem às matérias do usuário logado
    user_tasks = Tarefa.objects.filter(materia__usuario=request.user)
    
    total_tarefas = user_tasks.count()
    tarefas_concluidas = user_tasks.filter(status='C').count()
    
    # Prevenção de divisão por zero
    porcentagem_concluida = round((tarefas_concluidas / total_tarefas) * 100) if total_tarefas > 0 else 0

    # 1B. Dados Estatísticos de PROVAS (NOVO)
    user_provas = Prova.objects.filter(materia__usuario=request.user)
    total_provas = user_provas.count()
    
    # Conta provas que estão na data de hoje (>=) ou no futuro
    provas_futuras = user_provas.filter(data_prova__gte=timezone.now().date()).count() 

    # 2. Tarefas Urgentes e Próximas (Para o painel rápido)
    # Status 'A' (A Fazer) ou 'E' (Em Andamento)
    tarefas_urgentes = user_tasks.filter(status__in=['A', 'E'], prioridade='A').order_by('data_fim')[:5]
    tarefas_proximas = user_tasks.filter(status__in=['A', 'E']).order_by('data_fim')[:5]
    
    # 2B. Próximas PROVAS (NOVO)
    # Busca as 5 provas com data mais próxima (que ainda não passaram)
    proximas_provas = user_provas.filter(data_prova__gte=timezone.now().date()).order_by('data_prova')[:5]
    
    # 3. Distribuição por Matéria
    # Agrupa por matéria, contando total e pendentes
    distribuicao_materias = Materia.objects.filter(usuario=request.user).annotate(
        total_tarefas=Count('tarefas'),
        tarefas_pendentes=Count('tarefas', filter=Q(tarefas__status__in=['A', 'E']))
    ).order_by('-tarefas_pendentes')
    
    # 4. Contagem de Status (para possível uso em gráficos futuros)
    contagem_status = user_tasks.values('status').annotate(total=Count('status'))
    
    context = {
        # Dados de Tarefas
        'total_tarefas': total_tarefas,
        'tarefas_concluidas': tarefas_concluidas,
        'porcentagem_concluida': porcentagem_concluida,
        'tarefas_urgentes': tarefas_urgentes,
        'tarefas_proximas': tarefas_proximas,
        
        # Dados de Provas (ADICIONADOS)
        'total_provas': total_provas,
        'provas_futuras': provas_futuras,
        'proximas_provas': proximas_provas, 
        
        # Dados de Matérias/Status
        'materias': distribuicao_materias,
        'contagem_status': contagem_status,
        'all_materias': Materia.objects.filter(usuario=request.user).count()
    }
    return render(request, 'agenda/dashboard.html', context)

@login_required
def agenda(request):
    tarefas = Tarefa.objects.filter(materia__usuario=request.user)
    
    # Usa o serializador para transformar o QuerySet em JSON (com campos completos)
    tarefas_json = serializers.serialize('json', tarefas, 
        fields=('titulo', 'descricao', 'data_inicio', 'data_fim', 'status', 'materia'))

    context = {
        'tarefas_json': tarefas_json, # Envie o JSON serializado
        'materias': Materia.objects.filter(usuario=request.user),
    }
    return render(request, 'agenda/agenda.html', context)

# --- Novas Views para Gerenciamento de Matérias ---

@login_required
def materia_list(request):
    materias = Materia.objects.filter(usuario=request.user).order_by('nome')
    return render(request, 'agenda/materia_list.html', {'materias': materias})

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
    return render(request, 'agenda/materia_form.html', {'form': form, 'title': 'Nova Matéria'})

@login_required
def materia_update(request, pk):
    materia = get_object_or_404(Materia, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matéria atualizada com sucesso!')
            return redirect('materia_list')
    else:
        form = MateriaForm(instance=materia)
    return render(request, 'agenda/materia_form.html', {'form': form, 'title': 'Editar Matéria'})

@login_required
def materia_delete(request, pk):
    materia = get_object_or_404(Materia, pk=pk, usuario=request.user)
    if request.method == 'POST':
        materia.delete()
        messages.success(request, 'Matéria deletada com sucesso!')
        return redirect('materia_list')
    return render(request, 'agenda/materia_confirm_delete.html', {'materia': materia})

@login_required
def tarefa_list(request):
    # Pega a base de tarefas do usuário logado
    tarefas = Tarefa.objects.filter(materia__usuario=request.user)

    # Pega os valores dos filtros da URL (se existirem)
    materia_id = request.GET.get('materia')
    status = request.GET.get('status')
    prioridade = request.GET.get('prioridade')

    # Aplica os filtros na busca do banco de dados
    if materia_id:
        tarefas = tarefas.filter(materia__id=materia_id)
    if status:
        tarefas = tarefas.filter(status=status)
    if prioridade:
        tarefas = tarefas.filter(prioridade=prioridade)
    
    # Ordena o resultado final
    tarefas = tarefas.order_by('data_inicio')

    # Prepara o contexto para enviar ao template
    context = {
        'tarefas': tarefas,
        'all_materias': Materia.objects.filter(usuario=request.user), # Para o dropdown de matérias
        'status_choices': Tarefa.STATUS_CHOICES, # Para o dropdown de status
        'prioridade_choices': Tarefa.PRIORIDADE_CHOICES, # Para o dropdown de prioridade
        'current_filters': { # Para manter os filtros selecionados no formulário
            'materia': int(materia_id) if materia_id else None,
            'status': status,
            'prioridade': prioridade,
        }
    }
    return render(request, 'agenda/tarefa_list.html', context)

@login_required
def tarefa_create(request):
    if request.method == 'POST':
        # Passamos o request.user para o formulário
        form = TarefaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa criada com sucesso!')
            return redirect('tarefa_list')
    else:
        # Passamos o request.user para o formulário
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


# --- VIEWS PARA GERENCIAMENTO DE PROVAS (CRUD) ---

@login_required
def prova_list(request):
    # Lista provas que pertencem às matérias do usuário logado, ordenadas por data
    provas = Prova.objects.filter(materia__usuario=request.user).order_by('data_prova')
    
    # Filtro opcional por matéria
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
        
        if form.is_valid(): # Apenas verifica o form da Prova
            prova = form.save()
            
            messages.success(request, 'Prova agendada com sucesso! Adicione os materiais de apoio a seguir.')
            return redirect('material_list', prova_pk=prova.pk) 
    else:
        form = ProvaForm(user=request.user)
    
    context = {
        'form': form, 
        # O formset não é mais passado
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
            return redirect('prova_list') # Retorna para a lista principal
    else:
        form = ProvaForm(instance=prova, user=request.user)
        
    context = {
        'form': form, 
        'title': 'Editar Prova',
        'prova': prova # Passa a prova para redirecionamento após edição (opcional)
    }
    return render(request, 'agenda/prova_form.html', context)

@login_required
def prova_delete(request, pk):
    # Garante que o usuário só delete provas de suas matérias
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
def material_create(request, prova_pk):
    prova = get_object_or_404(Prova, pk=prova_pk, materia__usuario=request.user)
    
    if request.method == 'POST':
        form = MaterialDeApoioForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.prova = prova # Associa o material à prova correta
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
def material_delete(request, pk):
    material = get_object_or_404(MaterialDeApoio, pk=pk, prova__materia__usuario=request.user)
    
    if request.method == 'POST':
        prova_pk = material.prova.pk
        material.delete()
        messages.success(request, 'Material de apoio removido.')
        return redirect('material_list', prova_pk=prova_pk)
        
    return render(request, 'agenda/material_confirm_delete.html', {'material': material})