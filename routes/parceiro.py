import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader
from psycopg2.extras import RealDictCursor

from database.conexao import get_conexao, release_conexao

# Se essa função estiver em outro arquivo,
# depois ajustamos o import:
from funcoes.produto import contar_produtos

load_dotenv()

router = APIRouter()


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


CHAVE_PARCEIRO = os.getenv("API_KEY_PARCEIRO")



def validar_api_key_parceiro(
    api_key: str = Security(api_key_header)
):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key ausente."
        )

    if api_key != CHAVE_PARCEIRO:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida."
        )

    return True
    # Você pode retornar dados da chave para usar dentro das rotas (ex.: cnpj do integrador)
    return {"api_codigo": row[0], "api_cnpj": row[1]}



#------------------------------------------------------------  
# --- Rota 1: Buscar Produto por descricao-------------------
#------------------------------------------------------------
@router.get("/tabela_produtos/", dependencies=[Depends(validar_api_key_parceiro)])
def get_tabela_produtos(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    #limit=50, offset=0    → primeiros 50
    #limit=50, offset=50   → próximos 50
    #limit=50, offset=100  → próximos 50     

    conn = get_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    total = contar_produtos()

    try:
        cursor.execute(
            """
            SELECT 
            est_codigo,
            est_codfabricante,
            est_codoriginal,
            est_codreferencia,
            est_descricao,
            est_aplicacao,
            est_qtde,
            est_preco1,
            est_preco2,
            est_preco3,
            est_preco4,
            fabricante.fab_fabricante,
            segmentos.seg_segmento
            FROM estoque
            LEFT JOIN fabricante 
            ON fabricante.fab_codigo = estoque.est_fabricante
            LEFT JOIN segmentos 
            ON segmentos.seg_codigo = estoque.est_segmento
            ORDER BY est_descricao ASC
             LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="Produto não encontrado."
            )

        resultados = [
            {
                "codigo": r["est_codigo"],
                "codfabricante": r["est_codfabricante"],
                "codoriginal": r["est_codoriginal"],
                "codreferencia": r["est_codreferencia"],
                "descricao": r["est_descricao"],
                "aplicacao": r["est_aplicacao"],
                "fabricante": r["fab_fabricante"],
                "segmento": r["seg_segmento"],
                "qtde": r["est_qtde"],
                "preco1": r["est_preco1"],
                "preco2": r["est_preco1"],
                "preco3": r["est_preco1"],
                "preco4": r["est_preco1"],
                "encontrado": True
            }
            for r in rows
        ]

        return {
            
            "items": resultados,
            "offset": offset,
            "limit": limit,
            "count": total
        }

    finally:
        cursor.close()
        release_conexao(conn)
