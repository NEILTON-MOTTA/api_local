
from database.conexao import get_conexao, release_conexao,get_conexao_imagem, release_conexao_imagem


#-----------------------------------------------------------
# CMV 
#-----------------------------------------------------------
def retornar_cmv():
    conn = get_conexao()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
        select sum(ite_compra*ite_qtde) as xtot from item_prevenda
        inner join corpo_prevenda on corpo_prevenda.cor_numero =item_prevenda.ite_numero
        where corpo_prevenda.cor_data between date_trunc('month', CURRENT_DATE)
        AND CURRENT_DATE  and corpo_prevenda.cor_situacao = 'F'
       """)
        

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return resultado[0]

    finally:
        cursor.close()
        release_conexao(conn)


#-----------------------------------------------------------
# Compras
#-----------------------------------------------------------
def retornar_compras():
    conn = get_conexao()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
        Select sum(corpo_compra.cor_totalnota) as xtot   from  corpo_compra 
        where corpo_compra.cor_dataentrada between date_trunc('month', CURRENT_DATE)  AND CURRENT_DATE 
        and corpo_compra.cor_situacao = 'F' 
        """)
        

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return resultado[0]

    finally:
        cursor.close()
        release_conexao(conn)



        

#-----------------------------------------------------------
# Pagamento fornecedor
#-----------------------------------------------------------
def retornar_pagfornecedor():
    conn = get_conexao()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
        SELECT SUM(pagfat_valor) AS xtot   FROM pagamentos 
        where  pagfat_datapag  between date_trunc('month', CURRENT_DATE)  AND CURRENT_DATE  
        AND  (substr(pagfat_codconta,1,7) ='0003.01'or substr(pagfat_codconta,1,7) ='0004.01'  )
        """)
        

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return resultado[0]

    finally:
        cursor.close()
        release_conexao(conn)


#-----------------------------------------------------------
# VendaAcumuladaMes
#-----------------------------------------------------------
def retornar_vendaacumulada():
    conn = get_conexao()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
        select sum(COR_TOTAL) as xtot from corpo_prevenda
        where corpo_prevenda.cor_data between date_trunc('month', CURRENT_DATE)
        AND CURRENT_DATE  and corpo_prevenda.cor_situacao = 'F'
        """)
        

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return resultado[0]

    finally:
        cursor.close()
        release_conexao(conn)



#-----------------------------------------------------------
# Diferenca Percentual
#-----------------------------------------------------------
def diferenca_percentual(valor1: float, valor2: float) -> float:
    if valor1 > valor2:
        maior = valor1
        menor = valor2
    elif valor2 > valor1:
        maior = valor2
        menor = valor1
    else:
        return 0.0

    if maior > 0 and menor > 0:
        mdif = (maior - menor) * 100 / menor
        return round(mdif, 2)
    else:
        return 0.0

#-----------------------------------------------------------
# Markup
#-----------------------------------------------------------
def markup(preco_venda: float, preco_custo: float) -> float:
    try:
        valor = diferenca_percentual(preco_venda, preco_custo)
        return round(valor, 2)
    except Exception as erro:
        print(f"Erro ao calcular markup: {erro}")
        return 0.0


#-----------------------------------------------------------
# Markup
#-----------------------------------------------------------

def margem(preco_venda: float, preco_custo: float) -> float:
    if preco_venda <= 0:
        return 0.0

    diferenca = preco_venda - preco_custo
    valor_margem = (diferenca * 100) / preco_venda

    return round(valor_margem, 2) 
