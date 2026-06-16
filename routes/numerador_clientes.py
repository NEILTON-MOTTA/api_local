from fastapi import APIRouter, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from psycopg2.extras import RealDictCursor
from database.conexao import get_conexao, release_conexao

router = APIRouter()

# ===== Configuráveis =====
NUM_WIDTH = 6          # Quantidade de dígitos no retorno, ex.: 6 -> 000123
PREFIXO   = ""         # Se quiser, coloque algo tipo "CLI-"
# ========================

# Header da API Key (ajuste se necessário)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validar_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="API key ausente.")
    # (Opcional) validar no BD se a chave é válida/ativa
    return api_key

@router.put("/numerador_cliente/incrementar")
def incrementar_numerador(api_key: str = Security(validar_api_key)):
    conn = get_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            UPDATE numerador_clientes
               SET par_cliente = LPAD((COALESCE(par_cliente, '0')::int + 1)::text, 6, '0')
            RETURNING par_cliente;
        """)
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            raise HTTPException(status_code=500, detail="Nenhuma linha atualizada.")
        conn.commit()

        proximo_num = row["par_cliente"]                  # inteiro, ex.: 43
        proximo_fmt = f"{PREFIXO}{str(proximo_num).zfill(NUM_WIDTH)}"  # ex.: 000043 ou CLI-000043

        return {
            "mensagem": "par_cliente atualizado com sucesso",
            "novo_par_cliente": proximo_num,
            "novo_par_cliente_formatado": proximo_fmt
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {str(e)}")
    finally:
        cursor.close()
        release_conexao(conn)
