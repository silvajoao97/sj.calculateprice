from django.shortcuts import render, redirect
from django.db import connection
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
from .forms import dadoform


def calculo_de_coeficiente(Prim_DesDate, datapagamento, prazo, taxa, saldo):
    with connection.cursor() as cursor:
        cursor.execute('EXEC cauculatecoediciente @Prim_DesDate=%s, @datapagamento=%s, @prazo=%s, @taxa=%s, @saldo=%s', 
                       [Prim_DesDate, datapagamento, prazo, taxa, saldo])
        results = cursor.fetchall()
    return results

def calculo_de_coeficiente_resumido(Prim_DesDate, datapagamento, prazo, taxa, saldo):
    with connection.cursor() as cursor:
        cursor.execute('EXEC cauculatePmt @Prim_DesDate=%s, @datapagamento=%s, @prazo=%s, @taxa=%s, @saldo=%s', 
                       [Prim_DesDate, datapagamento, prazo, taxa, saldo])
        results = cursor.fetchall()
    return results

def coeficiente_view(request):
    # Adiciona um identificador de sessão
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    resultados = None
    pmt = None
    form = dadoform(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        Prim_DesDate = form.cleaned_data['Prim_DesDate']
        datapagamento = form.cleaned_data['datapagamento']
        prazo = form.cleaned_data['prazo']
        taxa = form.cleaned_data['taxa']
        saldo = form.cleaned_data['saldo']
        resultados = calculo_de_coeficiente(Prim_DesDate, datapagamento, prazo, taxa, saldo)
        pmt = calculo_de_coeficiente_resumido(Prim_DesDate, datapagamento, prazo, taxa, saldo)
        
        # Armazena os resultados e os dados do formulário no cache com a chave de sessão
        cache.set(f'resultados_cache_{session_key}', resultados, timeout=30)  # Cache por 15 minutos
        cache.set(f'form_data_cache_{session_key}', form.cleaned_data, timeout=30)  # Cache por 15 minutos
        cache.set(f'pmt_cache_{session_key}', pmt, timeout=30)  # Cache por 15 minutos

        #usado para fazer o formulário sempre retornar para a URL principal ao calcular 
        return redirect(request.path)
    
    # Tenta obter os resultados e os dados do formulário do cache
    if not resultados:
        resultados = cache.get(f'resultados_cache_{session_key}')
        form_data = cache.get(f'form_data_cache_{session_key}')
        pmt = cache.get(f'pmt_cache_{session_key}')
        if form_data:
            form = dadoform(initial=form_data)

    if resultados:
        paginator = Paginator(resultados, 20)  # Mostra 10 itens por página
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    else:
        page_obj = None

    return render(request, 'dado.html', {'form': form, 'resultados': page_obj, 'pmt': pmt})