from django import forms
from .models import Collection, Piece, PieceColor, PieceImage


class CollectionForm(forms.ModelForm):
    """Formulário para criar/editar coleções"""

    class Meta:
        model = Collection
        fields = [
            'name',
            'status',
            'notes',
            'expected_launch_date',
            'actual_launch_date',
            'modeling_time',
            'pilot_piece_time',
            'test_piece_time',
            'production_time',
            'preparation_time',
            'transportation_time',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome da Coleção'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Anotações sobre a coleção...'
            }),
            'expected_launch_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'actual_launch_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'modeling_time': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dias'
            }),
            'pilot_piece_time': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dias'
            }),
            'test_piece_time': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dias'
            }),
            'production_time': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dias'
            }),
            'preparation_time': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dias'
            }),
            'transportation_time': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dias'
            }),
        }
        labels = {
            'name': 'Nome da Coleção',
            'status': 'Status',
            'notes': 'Observações',
            'expected_launch_date': 'Data Prevista de Lançamento',
            'actual_launch_date': 'Data Real de Lançamento',
            'modeling_time': 'Tempo de Modelagem (dias)',
            'pilot_piece_time': 'Tempo de Peça Piloto (dias)',
            'test_piece_time': 'Tempo de Peça Teste (dias)',
            'production_time': 'Tempo de Produção (dias)',
            'preparation_time': 'Tempo de Preparação (dias)',
            'transportation_time': 'Tempo de Transporte (dias)',
        }


class PieceForm(forms.ModelForm):
    """Formulário para criar/editar peças"""

    class Meta:
        model = Piece
        fields = [
            'collection',
            'category',
            'fabric',
            'status',
            'sale_price',
            'total_cost',
            'fabric_consumption_p',
            'fabric_consumption_m',
            'fabric_consumption_g',
            'fabric_consumption_gg',
            'initial_quantity_p',
            'initial_quantity_m',
            'initial_quantity_g',
            'initial_quantity_gg',
            'accessories',
        ]
        widgets = {
            'collection': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'fabric': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'R$ 0,00'
            }),
            'total_cost': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'R$ 0,00'
            }),
            'fabric_consumption_p': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'Metros'
            }),
            'fabric_consumption_m': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'Metros'
            }),
            'fabric_consumption_g': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'Metros'
            }),
            'fabric_consumption_gg': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'placeholder': 'Metros'
            }),
            'initial_quantity_p': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Quantidade'
            }),
            'initial_quantity_m': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Quantidade'
            }),
            'initial_quantity_g': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Quantidade'
            }),
            'initial_quantity_gg': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Quantidade'
            }),
            'accessories': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'collection': 'Coleção',
            'category': 'Categoria',
            'fabric': 'Tecido',
            'status': 'Status',
            'sale_price': 'Preço de Venda',
            'total_cost': 'Custo Total',
            'fabric_consumption_p': 'Consumo de Tecido - P',
            'fabric_consumption_m': 'Consumo de Tecido - M',
            'fabric_consumption_g': 'Consumo de Tecido - G',
            'fabric_consumption_gg': 'Consumo de Tecido - GG',
            'initial_quantity_p': 'Quantidade Inicial - P',
            'initial_quantity_m': 'Quantidade Inicial - M',
            'initial_quantity_g': 'Quantidade Inicial - G',
            'initial_quantity_gg': 'Quantidade Inicial - GG',
            'accessories': 'Acessórios',
        }
