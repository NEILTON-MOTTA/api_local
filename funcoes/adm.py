
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



