from django import forms
from .models import Transferencia
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from django.forms.models import inlineformset_factory
from .models import Pessoa, Sancao, Eletronico, PDI
from django.core.validators import RegexValidator
class PessoaForm(forms.ModelForm):
    ESTUDANDO_CHOICES = [
        ('nao_estuda', 'Não'),
        ('ibraema', 'IBRAEMA'),
        ('eja_i', 'EJA I'),
        ('eja_ii', 'EJA II'),
        ('eja_iii', 'EJA III'),
        ('ensino_superior', 'Ensino Superior'),
    ]

    ESCOLARIDADE_CHOICES = [
        ('1', 'Fundamental Incompleto'),
        ('2', 'Fundamental Completo'),
        ('3', 'Médio Incompleto'),
        ('4', 'Médio Completo'),
        ('5', 'Superior Incompleto'),
        ('6', 'Superior Completo'),
    ]

    # Campos existentes
    nome_completo = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    data_nascimento = forms.DateField(required=False,widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )
    data_entrada = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    matricula = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Digite a matrícula"
    }),
    validators=[
        RegexValidator(regex=r'^\d{1,30}$', message="A matrícula deve conter apenas números (até 10 dígitos).")
    ]
)

    escolaridade = forms.ChoiceField(
        choices=ESCOLARIDADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    estudando = forms.ChoiceField(
        choices=ESTUDANDO_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    artigo_criminal = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    cidade = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    bloco = forms.ChoiceField(
        choices=Pessoa._meta.get_field('bloco').choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    cela = forms.ChoiceField(
        choices=Pessoa._meta.get_field('cela').choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )


    # Adicionando o campo saiu_temporariamente
    saiu_temporariamente = forms.BooleanField(
        required=False,
        label="Saiu Temporariamente",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

     # Adicionando o campo albergado
    albergado = forms.BooleanField(
        required=False,
        label="Albergado",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Pessoa
        fields = [
            'nome_completo',
            'data_nascimento',
            'matricula',
            'data_entrada',
            'escolaridade',
            'estudando',
            'artigo_criminal',
            'cidade',
            'bloco',
            'cela',
            'saiu_temporariamente',
            'albergado',  # Adicionando o campo albergado
        ]

class TransferenciaForm(forms.ModelForm):
    transferencia_ativa = forms.BooleanField(
        required=False,  # Checkbox é opcional
        label="Ativar Transferência",
        initial=False,  # Valor inicial do checkbox
    )

    class Meta:
        model = Transferencia
        fields = [
            'penitenciaria_destino', 
            'data_transferencia', 
            'justificativa',
            'transferencia_ativa',  # Adicionando o campo transferencia_ativa
        ]
        widgets = {
            'data_transferencia': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def save(self, commit=True):
        # Garantir que data_transferencia seja uma string válida
        data_transferencia = self.cleaned_data.get('data_transferencia')
        if data_transferencia:
            if isinstance(data_transferencia, str):
                data_transferencia = parse_datetime(data_transferencia)
            self.instance.data_transferencia = data_transferencia

        # Lidar com a transferência ativa
        transferencia_ativa = self.cleaned_data.get('transferencia_ativa')
        self.instance.transferencia_ativa = transferencia_ativa

        return super().save(commit)
    
class SancaoForm(forms.ModelForm):
    TIPOS_SANCAO = [
        ('sem_castelo', 'Sem Castelo'),
        ('sem_visita_intima', 'Sem Visita Íntima'),
        ('sem_visita_social', 'Sem Visita Social'),
        ('isolamento_preventivo', 'Isolamento Preventivo'),
        ('isolamento_reflexao', 'Isolamento Reflexão'),
    ]

    # Campo para escolher o tipo de sanção
    tipo = forms.ChoiceField(
        choices=TIPOS_SANCAO,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True
    )

    # Descrição da sanção
    descricao = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}),
        required=True
    )

    # Data de início e fim da sanção
    data_inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        required=True
    )
    data_fim = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        required=False
    )

    class Meta:
        model = Sancao
        fields = ['tipo', 'descricao', 'data_inicio', 'data_fim']

    def __init__(self, *args, **kwargs):
        super(SancaoForm, self).__init__(*args, **kwargs)
        # Se o formulário for instanciado para editar uma sanção já existente, preenche os campos com os dados da sanção
        if self.instance and self.instance.pk:
            self.fields['tipo'].initial = self.instance.tipo
            self.fields['descricao'].initial = self.instance.descricao
            self.fields['data_inicio'].initial = self.instance.data_inicio
            self.fields['data_fim'].initial = self.instance.data_fim
            
            
from django import forms
class PDIForm(forms.ModelForm):
    NATUREZA_PDI = [
        ('leve', 'Leve'),
        ('media', 'Média'),
        ('grave', 'Grave'),
    ]

    RESULTADOS_CHOICES = [
        ('andamento', 'Andamento'),
        ('condenado', 'Condenado'),
        ('sobrestado', 'Sobrestado',)
    ]

    # Novo campo para Nº PDI
    numero_pdi = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número do PDI"}),
        required=False
    )

    # Novo campo para Nº Ocorrência
    numero_ocorrencia = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número da Ocorrência"}),
        required=False
    )

    # Campo para Resultado
    resultado = forms.ChoiceField(
        choices=RESULTADOS_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    # Campo para natureza do PDI
    natureza = forms.ChoiceField(
        choices=NATUREZA_PDI,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    descricao = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Descreva o PDI..."}),
        required=False
    )

    data_inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        required=False
    )
    data_fim = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        required=False
    )

    pessoa = forms.ModelChoiceField(
    queryset=Pessoa.objects.all(),
    widget=forms.Select(attrs={"class": "form-control", "readonly": "readonly"}),  # Tornando o campo somente leitura
    required=True
)

    class Meta:
        model = PDI
        fields = ['numero_pdi', 'numero_ocorrencia', 'natureza', 'descricao', 'data_inicio', 'data_fim', 'pessoa', 'resultado']

    def __init__(self, *args, **kwargs):
        super(PDIForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['numero_pdi'].initial = self.instance.numero_pdi
            self.fields['numero_ocorrencia'].initial = self.instance.numero_ocorrencia
            self.fields['natureza'].initial = self.instance.natureza
            self.fields['descricao'].initial = self.instance.descricao
            self.fields['data_inicio'].initial = self.instance.data_inicio
            self.fields['data_fim'].initial = self.instance.data_fim
            self.fields['pessoa'].initial = self.instance.pessoa  # Preenche o campo com o valor atual da instância
            self.fields['resultado'].initial = self.instance.resultado
       
from django.core.exceptions import ValidationError

class EletronicoForm(forms.ModelForm):
    TIPOS_ELETRONICO = [
        ('tv', 'Tv'),
        ('radio', 'Rádio'),
        ('ventilador', 'Ventilador'),  # Novo tipo
    ]

    pessoa = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_pessoa",
            "autocomplete": "off",
            "placeholder": "Digite para buscar uma pessoa..."
        }),
        required=True,
        label="Selecionar Pessoa"
    )

    tipo = forms.ChoiceField(
        choices=TIPOS_ELETRONICO,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )

    nova_fiscal = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
        required=False
    )

    data_entrada = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False
    )

    class Meta:
        model = Eletronico
        fields = ['pessoa', 'tipo', 'data_entrada', 'nova_fiscal']
    
    # Validação customizada para garantir que não haja duplicidade de tipos por pessoa
    def clean(self):
        cleaned_data = super().clean()
        pessoa = cleaned_data.get('pessoa')
        tipo = cleaned_data.get('tipo')

        if pessoa and tipo:
            # Verifica se já existe um eletrônico do mesmo tipo para a mesma pessoa
            if Eletronico.objects.filter(pessoa=pessoa, tipo=tipo).exists():
                raise ValidationError(f"O Interno {pessoa.nome_completo} já possui um(a) {tipo} cadastrado(a).")

        return cleaned_data


from django import forms
from .models import FrenteDeTrabalho

class FrenteDeTrabalhoForm(forms.ModelForm):
    class Meta:
        model = FrenteDeTrabalho
        fields = ['pessoa', 'frente_trabalho', 'data_inicio', 'numero_portaria_admissao', 'data_retroacao']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_retroacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
