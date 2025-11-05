# Em agenda/models.py

from django.db import models
from django.contrib.auth.models import User

class Materia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nomenclatura = models.CharField(max_length=10, blank=True, verbose_name="Sigla")
    nome = models.CharField(max_length=100)
    
    notas_materia = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Anotações da Matéria"
    )
    
    link_plano_ensino = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Link do Plano de Ensino"
    )

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
    
    link_anexo = models.URLField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Link de Anexo/Material de Apoio"
    )

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['data_inicio']
        
class Prova(models.Model):
    materia = models.ForeignKey(
        'Materia', 
        on_delete=models.CASCADE, 
        related_name='provas',
        verbose_name="Matéria"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título da Prova")
    data_prova = models.DateField(
        verbose_name="Data da Prova",
        blank=True, 
        null=True 
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    link_anexos = models.URLField(max_length=200, blank=True, null=True, verbose_name="Link para Anexos (Drive/Lista)")
    
    def __str__(self):
        return f"{self.titulo} ({self.materia.nome})"

    class Meta:
        verbose_name_plural = "Provas"
        ordering = ['data_prova']
        
class MaterialDeApoio(models.Model):
    # TIPO_CHOICES original mantido para compatibilidade com dados existentes, mas form usa simplificado
    TIPO_CHOICES = [
        ('LINK', 'Link Externo'),
        ('PDF', 'Arquivo PDF'),
        ('TXT', 'Texto/Anotação'),
        ('OUTRO', 'Outro Arquivo'),
    ]

    prova = models.ForeignKey(
        'Prova',
        on_delete=models.CASCADE,
        related_name='materiais',
        verbose_name="Prova Relacionada"
    )
    
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES, default='LINK', verbose_name="Tipo de Material")
    
    link_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL do Recurso")
    
    arquivo = models.FileField(
        upload_to='materiais_provas/', 
        blank=True, 
        null=True, 
        verbose_name="Anexo de Arquivo"
    )
    
    titulo = models.CharField(max_length=255, verbose_name="Título do Material")

    def __str__(self):
        return f"{self.titulo} para {self.prova.titulo}"

    class Meta:
        verbose_name_plural = "Materiais de Apoio"
        
        
class HorarioAula(models.Model):
    DIAS_SEMANA = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]
    
    materia = models.ForeignKey(
        'Materia', 
        on_delete=models.CASCADE, 
        related_name='horarios',
        verbose_name="Matéria"
    )
    dia_semana = models.CharField(max_length=3, choices=DIAS_SEMANA, verbose_name="Dia da Semana")
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    local = models.CharField(max_length=50, blank=True, null=True, verbose_name="Local/Sala")

    def __str__(self):
        return f"{self.materia.nome} ({self.dia_semana} {self.hora_inicio})"

    class Meta:
        verbose_name_plural = "Horários de Aula"
        ordering = ['dia_semana', 'hora_inicio']
