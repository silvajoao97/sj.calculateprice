from django import forms

class dadoform(forms.Form):
    Prim_DesDate = forms.DateField(label='Data 1° Desconto', widget=forms.DateInput(attrs={'type': 'date'}))
    datapagamento = forms.DateField(label='Data Pagamento',widget=forms.DateInput(attrs={'type': 'date'}))
    prazo = forms.IntegerField(label='Prazo', max_value=100)
    taxa = forms.FloatField(label='Taxa %', max_value=29)
    saldo = forms.DecimalField(label='Saldo R$', max_digits=10, decimal_places=2)
