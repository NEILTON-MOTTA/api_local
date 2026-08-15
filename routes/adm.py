# routes/estoque.py
from fastapi import APIRouter, Depends, HTTPException,Body, Security, status,Query
from fastapi.security.api_key import APIKeyHeader
from database.conexao import get_conexao, release_conexao,get_conexao_imagem, release_conexao_imagem
from psycopg2.extras import RealDictCursor
import re
from typing import Dict, Any
from psycopg2 import errors
from fastapi.responses import Response
from funcoes.adm import retornar_cmv,retornar_compras,retornar_pagfornecedor,retornar_vendaacumulada
from funcoes.adm import markup,margem,diferenca_percentual





router = APIRouter()

# ===== Configuráveis =====
NUM_WIDTH = 6          # Quantidade de dígitos no retorno, ex.: 6 -> 000123
PREFIXO   = ""         # Se quiser, coloque algo tipo "CLI-"
# ========================


# Lê a chave do header X-API-Key (pode trocar o nome se preferir)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validar_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key ausente (use o header X-API-Key)."
        )

    conn = get_conexao()
    cursor = conn.cursor()
    try:
    
        cursor.execute("""
            SELECT api_codigo, api_cnpj
            FROM api_key
            WHERE api_key = %s
              AND (ativo = TRUE OR ativo IS NULL)
            LIMIT 1
        """, (api_key,))
        row = cursor.fetchone()
    finally:
        cursor.close()
        release_conexao(conn)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida."
        )

    # Você pode retornar dados da chave para usar dentro das rotas (ex.: cnpj do integrador)
    return {"api_codigo": row[0], "api_cnpj": row[1]}

# Aplica a validação de API key em TODO o router



# ---------------------------------------
# --- Rota 1: CMV X COMPRAS--
# ---------------------------------------
@router.get("/cmvcompras", dependencies=[Depends(validar_api_key)])
def get_cmv_x_compras():
        
    #conn = get_conexao()
    #cur = conn.cursor(cursor_factory=RealDictCursor)

    
    cmv = retornar_cmv()
    compras=retornar_compras()
    venda=retornar_vendaacumulada()
    return {
            "CMV":cmv,
            "compras":compras,
            "venda":venda,
            "encontrado":True

     }
    


# -----------------------------------------
# --- Rota 1: CMV X pagamento fornecedor--
# -----------------------------------------
@router.get("/cmvfornecedor", dependencies=[Depends(validar_api_key)])
def get_cmv_x_pagfornecedor():
        
    #conn = get_conexao()
    #cur = conn.cursor(cursor_factory=RealDictCursor)

    
    cmv = retornar_cmv()
    pagforn=retornar_pagfornecedor()
    venda=retornar_vendaacumulada()
    return {
            "CMV":cmv,
            "Pagfornecedor":pagforn,
            "venda":venda,
            "encontrado":True

     }
    
   
    

# ---------------------------------------
# --- Rota 1: Buscar vendas diaria-------
# ---------------------------------------
@router.get("/venda_diaria", dependencies=[Depends(validar_api_key)])
def get_venda_por_dia():
    
    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
          select cor_data,sum(cor_total) as xtotavendas,Sum(cor_volume) as xvol,count(cor_numero) as xqtdevendas,sum(cor_cmv) as xcmv,sum(cor_totalfrete) as xfrete from corpo_prevenda
          where corpo_prevenda.cor_data between date_trunc('month', CURRENT_DATE)
          AND CURRENT_DATE  and corpo_prevenda.cor_situacao = 'F'
          group by  cor_data order by cor_data

        """, ())

        
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="venda não encontrado."
            )

        resultados = []

        for registro in rows:
            
            venda_liquida: float = float(registro["xtotavendas"]  or 0) - float(registro["xfrete"]  or 0)
            qtde_vendas: float = float(registro["xqtdevendas"]  or 0)
            cmv: float = float(registro["xcmv"]  or 0)
            
            markup_real: float = markup(venda_liquida, cmv)
            margem_real: float = margem(venda_liquida, cmv)
            
            ticketmedio: float
            
            if venda_liquida > 0 and qtde_vendas > 0:
                ticketmedio = venda_liquida / qtde_vendas
            else:
                ticketmedio = 0.0


                
           
            resultados.append({
                "data": registro["cor_data"],
                "vendas": registro["xtotavendas"],
                "volume": registro["xvol"],
                "qtde_vendas": registro["xqtdevendas"],
                "ticketmedio": round(ticketmedio, 2),
                "markup": round(markup_real, 2),
                "margem": round(margem_real, 2),
                "cmv": round(cmv, 2),
                "encontrado": True
            })

        return {
            
            "items": resultados
        }

    finally:
        cur.close()
        release_conexao(conn)


    
# ---------------------------------------------------------
# --- Rota 1: Buscar Fluxo de caixa - Entradas ------------
# ---------------------------------------------------------
@router.get("/fluxo_caixa_entradas", dependencies=[Depends(validar_api_key)])
def get_fluxo_caixa_entradas():
    
    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
        Select cai_tipo,sum(cai_entrada) as xtot FROM caixa
        where (cai_data=CURRENT_DATE)
        and (substr(cai_movimento,1,2) <>'AC' AND  substr(cai_movimento,1,2) <>'EC' )
        and cai_entrada> 0 
        Group by cai_tipo
        """, ())

        
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="venda não encontrado."
            )

        resultados = []

        for registro in rows:
            
            total_formapag: float = float(registro["xtot"]  or 0)
                   
            resultados.append({
                "Forma": registro["cai_tipo"],
                "Valor":  round(total_formapag, 2),
                "encontrado": True
            })

        return {
            
            "items": resultados
        }

    finally:
        cur.close()
        release_conexao(conn)
    

# ---------------------------------------------------------
# --- Rota 1: Buscar Fluxo de caixa - saidas ------------
# ---------------------------------------------------------
@router.get("/fluxo_caixa_saidas", dependencies=[Depends(validar_api_key)])
def get_fluxo_caixa_saidas():
    
    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
        Select cai_descricao ,cai_tipo,cai_saida FROM caixa
        where (cai_data=CURRENT_DATE) AND cai_saida>0 AND SUBSTR(cai_movimento,1,2) <>'EC'
        """, ())

        
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="venda não encontrado."
            )

        resultados = []

        for registro in rows:
            
            valor_saida: float = float(registro["cai_saida"]  or 0)
                   
            resultados.append({
                "descricao": registro["cai_descricao"],
                "forma": registro["cai_tipo"],
                "valor":  round(valor_saida, 2),
                "encontrado": True
            })

        return {
            
            "items": resultados
        }

    finally:
        cur.close()
        release_conexao(conn)
    


# ---------------------------------------------------------
# --- Rota 1: Buscar contas_pagar - abertas ---------------
# ---------------------------------------------------------
@router.get("/contas_pagar_abertas", dependencies=[Depends(validar_api_key)])
def get_contas_pagar_abertas():
    
    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
        Select pag_datapagar, pag_descricao,pag_valor from contas_pagar
        where pag_datapagar =current_date and pag_situacao=0
        """, ())

        
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="venda não encontrado."
            )

        resultados = []

        for registro in rows:
            
            valor_fatura: float = float(registro["pag_valor"]  or 0)
                   
            resultados.append({
                "vencimento": registro["pag_datapagar"],
                "descricao": registro["pag_descricao"],
                "valor":  round(valor_fatura, 2),
                "encontrado": True
            })

        return {
            
            "items": resultados
        }

    finally:
        cur.close()
        release_conexao(conn)
    



