# Em agenda/models.py
from django.db import models
from django.contrib.auth.models import User

class Materia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nomenclatura = models.CharField(max_length=10, blank=True, verbose_name="Sigla")
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({self.nomenclatura})"

    class Meta:
        verbose_name_plural = "Matérias"

class Tarefa(models.Model):
    STATUS_CHOICES = [('A', 'A Fazer'), ('E', 'Em Andamento'), ('C', 'Concluída')]
    PRIORIDADE_CHOICES = [('B', 'Baixa'), ('M', 'Média'), ('A', 'Alta')]
    
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='tarefas')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateTimeField(verbose_name="Data de Início")
    data_fim = models.DateTimeField(verbose_name="Data de Fim")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    prioridade = models.CharField(max_length=1, choices=PRIORIDADE_CHOICES, default='M')

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['data_inicio']