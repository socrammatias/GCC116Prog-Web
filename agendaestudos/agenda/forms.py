# Em agenda/forms.py

from django import forms
from .models import Materia
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tarefa # Adicione este import

# --- ESTA CLASSE FOI ATUALIZADA ---
class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['nome', 'nomenclatura']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cálculo I'}),
            'nomenclatura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: MAT140'}),
        }
        labels = {
            'nome': 'Nome da Matéria',
            'nomenclatura': 'Sigla (Opcional)',
        }

# --- ESTA CLASSE CONTINUA IGUAL ---
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Traduzir e customizar os campos
        self.fields['username'].label = "Nome de Usuário"
        self.fields['username'].help_text = None # Remove o texto de ajuda longo

        self.fields['password1'].label = "Senha"
        
        self.fields['password2'].label = "Confirmação de Senha"

        # Adicionar a classe do Bootstrap a todos os campos para estilização
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
class TarefaForm(forms.ModelForm):
    # Usando um widget para ter um seletor de data e hora mais amigável
    data_inicio = forms.DateTimeField(
        label='Data de Início',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    data_fim = forms.DateTimeField(
        label='Data de Fim',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Pega o 'user' que foi passado pela view
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtra o campo 'materia' para mostrar apenas as matérias do usuário logado
        if user:
            self.fields['materia'].queryset = Materia.objects.filter(usuario=user)
        
        # Adiciona a classe do bootstrap nos outros campos
        self.fields['materia'].widget.attrs.update({'class': 'form-select'})
        self.fields['titulo'].widget.attrs.update({'class': 'form-control'})
        self.fields['descricao'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['prioridade'].widget.attrs.update({'class': 'form-select'})


    class Meta:
        model = Tarefa
        fields = ['materia', 'titulo', 'descricao', 'data_inicio', 'data_fim', 'status', 'prioridade']