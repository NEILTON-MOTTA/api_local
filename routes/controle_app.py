# routes/estoque.py
from fastapi import APIRouter, Depends, HTTPException,Body, Security, status,Query
from fastapi.security.api_key import APIKeyHeader
from database.conexao import get_conexao, release_conexao
from psycopg2.extras import RealDictCursor
import re
from typing import Dict, Any
from psycopg2 import errors




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
# --- Rota 1: Buscar Produto por codigo--
# ---------------------------------------
@router.get("/empresa_cnpj/{cnpj}", dependencies=[Depends(validar_api_key)])
def get_empresa_por_cnpj(cnpj: str):
    cnpj_empresa = re.sub(r"\D", "", cnpj or "")
    if len(cnpj_empresa) != 14:
        raise HTTPException(status_code=400, detail="Cnpj inválido (use 14 dígitos).")

    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
    SELECT ctl_cnpj, ctl_empresa, ctl_endpoint, ctl_ativo
    FROM api_controle_app
    WHERE ctl_cnpj = %s
    LIMIT 1
   """, (cnpj_empresa,))
        empresa = cur.fetchone()
    finally:
        cur.close()
        release_conexao(conn)

    if empresa:
        return {
                 "cnpj": empresa["ctl_cnpj"],
                 "empresa": empresa["ctl_empresa"],
                 "endpoint": empresa["ctl_endpoint"],
                 "ativo": empresa["ctl_ativo"],
                 "encontrado":True
        }

    else:
        raise HTTPException(status_code=404, detail="Empresa não encontrado")
    

