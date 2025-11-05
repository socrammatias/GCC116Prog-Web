from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Materia, Tarefa, Prova, MaterialDeApoio, HorarioAula 


# --- NOVO: CustomLoginForm para simetria na tela de login ---
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].label = "Usuário"
        self.fields['password'].label = "Senha"
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control'
        })


# --- CustomUserCreationForm (Cadastro) ---
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].label = "Nome de Usuário"
        self.fields['username'].help_text = None

        self.fields['password1'].label = "Senha"
        self.fields['password2'].label = "Confirmação de Senha"

        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)


# --- MateriaForm (RESTAURADO PARA O MÍNIMO) ---
class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        # CAMPOS LIMPOS (Sem notas fixas e sem horário fixo)
        fields = ['nome', 'nomenclatura', 'notas_materia', 'link_plano_ensino'] 
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cálculo I'}),
            'nomenclatura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: MAT140'}),
            'notas_materia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Professor, horário, ementa, etc.'}),
            'link_plano_ensino': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Cole o link do Plano de Ensino'}),
        }
        labels = {
            'nome': 'Nome da Matéria',
            'nomenclatura': 'Sigla (Opcional)',
            'notas_materia': 'Anotações da Matéria',
            'link_plano_ensino': 'Plano de Ensino (Link)',
        }
        
# --- TarefaForm ---
class TarefaForm(forms.ModelForm):
    data_inicio = forms.DateTimeField(
        label='Data de Início',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    data_fim = forms.DateTimeField(
        label='Data de Fim',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['materia'].queryset = Materia.objects.filter(usuario=user)
        
        self.fields['materia'].widget.attrs.update({'class': 'form-select'})
        self.fields['titulo'].widget.attrs.update({'class': 'form-control'})
        self.fields['descricao'].widget.attrs.update({'class': 'form-control'})
        self.fields['link_anexo'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Link para o material ou fonte da tarefa'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['prioridade'].widget.attrs.update({'class': 'form-select'})

    class Meta:
        model = Tarefa
        fields = ['materia', 'titulo', 'descricao', 'data_inicio', 'data_fim', 'status', 'prioridade', 'link_anexo']
        
# --- ProvaForm ---
class ProvaForm(forms.ModelForm):
    data_prova = forms.DateField(
        label='Data da Prova',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False 
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['materia'].queryset = Materia.objects.filter(usuario=user)

        self.fields['materia'].widget.attrs.update({'class': 'form-select'})
        self.fields['titulo'].widget.attrs.update({'class': 'form-control'})
        self.fields['observacoes'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Prova
        fields = ['materia', 'titulo', 'data_prova', 'observacoes'] 


# --- Formulário de Material de Apoio ---
class MaterialDeApoioForm(forms.ModelForm):
    class Meta:
        model = MaterialDeApoio
        fields = ['titulo', 'link_url']  # <-- apenas título e link
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Aula 3 - Revisão para a prova'
            }),
            'link_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: https://drive.google.com/... ou https://youtu.be/...'
            }),
        }
        labels = {
            'titulo': 'Título do Material',
            'link_url': 'Link (YouTube, Drive, etc.)',
        }

    def clean(self):
        cleaned_data = super().clean()
        link_url = cleaned_data.get('link_url')

        if not link_url:
            raise forms.ValidationError("Por favor, insira um link válido para o material de apoio.")
        return cleaned_data
        
# --- FORMSET BASE ---
MaterialDeApoioFormSet = inlineformset_factory(
    Prova, 
    MaterialDeApoio, 
    form=MaterialDeApoioForm,
    extra=1, 
    can_delete=True 
)

# --- NOVO FORMULÁRIO PARA HORÁRIO DE AULA (Para Formset) ---
class HorarioAulaForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        # REMOVEMOS HORA_FIM DO MODELO PARA SIMPLIFICAR, mas ele ainda pode estar no BD
        # Vamos manter o fields:
        fields = ['dia_semana', 'hora_inicio', 'local']
        widgets = {
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 
            'local': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sala 301 / Zoom'}),
        }

# --- NOVO FORMSET PARA HORÁRIOS ---
HorarioAulaFormSet = inlineformset_factory(
    Materia,
    HorarioAula,
    form=HorarioAulaForm,
    extra=1,
    can_delete=True
)