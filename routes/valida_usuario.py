from fastapi import APIRouter, Depends, HTTPException, Security, status,Query
from fastapi.security.api_key import APIKeyHeader
from database.conexao import get_conexao, release_conexao
from psycopg2.extras import RealDictCursor
import re
router = APIRouter()


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
        # Ajuste o nome da tabela/campos conforme seu schema.
        # Ex.: adiciona um campo 'ativo' para poder revogar chaves.
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

# --- Rota 2: Buscar cliente por CNPJ ---

# Aplica a validação de API key em TODO o router


# -----------------------------------------
# --- Rota 1: valida senha ---
# -----------------------------------------

@router.get("/valida_auth/{login}/{senha}")
#def get_senha(senha: str):
def valida_login_get(login: str, senha: str, _apikey = Depends(validar_api_key)):
    #Converte para maiusculo
    login = (login or "").strip().upper()
    senha = (senha or "").strip().upper()
    
    # Pega a conexão do pool
    conn = get_conexao()
    cursor = conn.cursor()
    
    
    # Busca o cliente no banco (exemplo de campos: cli_codigo, nome, email)
    cursor.execute("""
            SELECT   usu_login, usu_grupo, fun_nome
            FROM usuarios left join funcionario on funcionario.fun_login=usuarios.usu_codigo
            WHERE usu_login = %s AND usu_senha = %s
            LIMIT 1
        
    """, (login, senha))
    senha = cursor.fetchone()
    
    cursor.close()
    release_conexao(conn)
    
    # Retorna mantendo o mesmo estilo da rota original
    if senha:
        
        if senha[1] == 0 or senha[1] == 1:
           strperfil = "ADMIN"
        else:
           strperfil = "USER"
           
        return {
                 "usuario": senha[0],
                 "perfil": strperfil,
                 "nome": senha[2],
                 "encontrou":"true"
                }
    else:
        return {
            "Senha": senha,
            "teste": "cliente não encontrado",
            "eof":"false"
        }
