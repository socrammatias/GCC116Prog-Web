# Em agenda/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('agenda/', views.agenda, name='agenda'),
    
    # Rotas de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='agenda/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # ADICIONE AS ROTAS PARA MATÉRIAS (CRUD)
    path('materias/', views.materia_list, name='materia_list'),
    path('materias/nova/', views.materia_create, name='materia_create'),
    path('materias/editar/<int:pk>/', views.materia_update, name='materia_update'),
    path('materias/deletar/<int:pk>/', views.materia_delete, name='materia_delete'),
    
    # --- ROTAS PARA PROVAS (CRUD) ---
    path('provas/', views.prova_list, name='prova_list'),
    path('provas/nova/', views.prova_create, name='prova_create'),
    path('provas/editar/<int:pk>/', views.prova_update, name='prova_update'),
    path('provas/deletar/<int:pk>/', views.prova_delete, name='prova_delete'),
    
    # --- ROTAS PARA MATERIAL DE APOIO ---
    path('provas/<int:prova_pk>/materiais/', views.material_list, name='material_list'),
    path('provas/<int:prova_pk>/materiais/nova/', views.material_create, name='material_create'),
    path('materiais/<int:pk>/deletar/', views.material_delete, name='material_delete'), # Não precisa do PK da prova aqui

    path('tarefas/', views.tarefa_list, name='tarefa_list'),
    path('tarefas/nova/', views.tarefa_create, name='tarefa_create'),
    path('tarefas/editar/<int:pk>/', views.tarefa_update, name='tarefa_update'),
    path('tarefas/deletar/<int:pk>/', views.tarefa_delete, name='tarefa_delete'),
]