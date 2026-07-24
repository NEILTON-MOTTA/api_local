# routes/estoque.py
from fastapi import APIRouter, Depends, HTTPException,Body, Security, status,Query
from fastapi.security.api_key import APIKeyHeader
from database.conexao import get_conexao, release_conexao,get_conexao_imagem, release_conexao_imagem
from psycopg2.extras import RealDictCursor
import re
from typing import Dict, Any
from psycopg2 import errors
from fastapi.responses import Response
from funcoes.adm import retornar_cmv,retornar_compras,retornar_pagfornecedor





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
    return {
            "CMV":cmv,
            "compras":compras,
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
    return {
            "CMV":cmv,
            "Pagfornecedor":pagforn,
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
        select cor_data,sum(cor_total) as xtot,Sum(cor_volume) as xvol,count(cor_numero) as xtotalvendas from corpo_prevenda 
        where cor_data between date_trunc('month', CURRENT_DATE)  AND CURRENT_DATE  and cor_situacao='F'  group by  cor_data order by cor_data

        """, ())

        
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="venda não encontrado."
            )

        resultados = []

        for r in rows:

            if r["xtotalvendas"] > 0 and r["xtot"] > 0:
                ticketmedio = r["xtot"] / r["xtotalvendas"]
            else:
                ticketmedio = 0

            resultados.append({
                "data": r["cor_data"],
                "vendas": r["xtot"],
                "volume": r["xvol"],
                "qtde_vendas": r["xtotalvendas"],
                "ticketmedio": round(ticketmedio, 2),
                "encontrado": True
            })

        return {
            
            "items": resultados
        }

    finally:
        cur.close()
        release_conexao(conn)
    
