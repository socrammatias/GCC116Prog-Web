# Este é o conteúdo COMPLETO e CORRETO para agenda/views.py

# --- Bloco de Imports Limpo e Organizado ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Materia
from .forms import CustomUserCreationForm, MateriaForm
from .models import Tarefa # Verifique se já não importou
from .forms import TarefaForm # Adicione este import

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
def home(request):
    return render(request, 'agenda/home.html')

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