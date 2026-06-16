# routes/estoque.py
from fastapi import APIRouter, Depends, HTTPException,Body, Security, status,Query
from fastapi.security.api_key import APIKeyHeader
from database.conexao import get_conexao, release_conexao
from psycopg2.extras import RealDictCursor
import re
from typing import Dict, Any
from psycopg2 import errors
from funcoes.produto import buscar_quantidade_produto



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
@router.get("/produto_codigo/{codigo}", dependencies=[Depends(validar_api_key)])
def get_produto_por_codigo(codigo: str):
    codigo_produto = re.sub(r"\D", "", codigo or "")
    if len(codigo_produto) != 6:
        raise HTTPException(status_code=400, detail="Codigo Produto inválido (use 6 dígitos).")

    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
    SELECT est_codigo, est_descricao,est_qtde
    FROM estoque
    WHERE est_codigo = %s
    LIMIT 1
   """, (codigo_produto,))
        produto = cur.fetchone()
    finally:
        cur.close()
        release_conexao(conn)

    if produto:
        return {
                 "__codigo": produto["est_codigo"],
                 "__descricao": produto["est_descricao"],
                 "__qtde": produto["est_qtde"],
                 "__retorno":"1"
        }

    else:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    


# -----------------------------------------------
# --- Rota 2: Buscar Produto por codFabricante--
# -----------------------------------------------
@router.get("/produto_codfabricante/{codfabricante}", dependencies=[Depends(validar_api_key)])
def get_produto_por_codfabricante(codfabricante: str):
    
    codfab_produto=(codfabricante or "").strip().upper()
    
    
    
    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
    SELECT est_codigo, est_descricao,est_aplicacao,est_qtde,est_preco1,est_margem1,est_preco2,est_margem2,est_preco3,est_margem3,est_preco4,est_margem4,
    fabricante.fab_fabricante,segmentos.seg_segmento
    FROM estoque left join  fabricante on fabricante.fab_codigo=estoque.est_fabricante
    left join  segmentos on segmentos.seg_codigo=estoque.est_segmento
    WHERE est_codfabricante = %s
    
   """, (codfab_produto,))
        produto = cur.fetchone()
    finally:
        cur.close()
        release_conexao(conn)

    if produto:
        return {
                 "codigo": produto["est_codigo"],
                 "descricao": produto["est_descricao"],
                 "aplicacao": produto["est_aplicacao"],
                 "fabricante": produto["fab_fabricante"],
                 "segmento": produto["seg_segmento"],
                 "qtde": produto["est_qtde"],
                 "preco1": produto["est_preco1"],
                 "margem1": produto["est_margem1"],
                 "preco2": produto["est_preco2"],
                 "margem2": produto["est_margem2"],
                 "preco3": produto["est_preco3"],
                 "margem3": produto["est_margem3"],
                 "preco4": produto["est_preco4"],
                 "margem4": produto["est_margem4"],
                 "encontrado":"true"
        }

    else:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    


# -----------------------------------------------
# --- Rota 3: Baixa no estoque-------------------
# -----------------------------------------------
@router.put("/baixar_produto/{codigo}/{quantidade}")
def put_baixar_qtde(
    codigo: str,
    quantidade: int,
    api_key: str = Security(validar_api_key)
):

    codigo_produto = re.sub(r"\D", "", codigo or "")

    if len(codigo_produto) != 6:
        raise HTTPException(
            status_code=400,
            detail="Codigo Produto inválido (use 6 dígitos)."
        )

    conn = get_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:

        cursor.execute("""
            UPDATE estoque
               SET est_qtde = est_qtde - %s
             WHERE est_codigo = %s
               AND est_qtde >= %s
         RETURNING est_qtde
        """, (
            quantidade,
            codigo_produto,
            quantidade
        ))

        row = cursor.fetchone()

        if not row:
            conn.rollback()

            raise HTTPException(
                status_code=500,
                detail="Nenhuma linha atualizada."
            )

        #-----------------------------------------------------
        # GERA LOG
        #-----------------------------------------------------
        sql_log = """
            INSERT INTO api_produtos_log (
                log_data,
                log_hora,
                log_codigo,
                log_operacao,
                log_qtde
            )
            VALUES (
                CURRENT_DATE,
                CURRENT_TIME,
                %s,
                %s,
                %s
            )
        """

        dados_log = (
            codigo_produto,
            'baixa estoque',
            quantidade
        )

        cursor.execute(sql_log, dados_log)
        #-----------------------------------------------------




        
        

        conn.commit()

        proximo_num = row["est_qtde"]

        return {
            "mensagem": "estoque atualizado com sucesso",
            "nova_qtde": proximo_num
        }

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar: {str(e)}"
        )

    finally:

        cursor.close()
        release_conexao(conn)


# -----------------------------------------------
# --- Rota 4: Inventario no estoque--------------
# -----------------------------------------------


@router.put("/inventario_produto/{codigo}/{quantidade}")
def put_inventario_qtde(
    codigo: str,
    quantidade: int,
    api_key: str = Security(validar_api_key)
):

    codigo_produto = re.sub(r"\D", "", codigo or "")

    if len(codigo_produto) != 6:
        raise HTTPException(
            status_code=400,
            detail="Codigo Produto inválido (use 6 dígitos)."
        )

    qtdeAnterior = buscar_quantidade_produto(codigo_produto)
    conn = get_conexao()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:

        cursor.execute("""
            UPDATE estoque
               SET est_qtde =  %s
             WHERE est_codigo = %s
             RETURNING est_qtde
        """, (
            quantidade,
            codigo_produto
            
        ))

        row = cursor.fetchone()

        if not row:
            conn.rollback()

            raise HTTPException(
                status_code=500,
                detail="Nenhuma linha atualizada."
            )

        #-----------------------------------------------------
        # GERA LOG
        #-----------------------------------------------------
        sql_log = """
            INSERT INTO api_produtos_log (
                log_data,
                log_hora,
                log_codigo,
                log_operacao,
                log_qtde
            )
            VALUES (
                CURRENT_DATE,
                CURRENT_TIME,
                %s,
                %s,
                %s
            )
        """

        dados_log = (
            codigo_produto,
            'INVENTARIO',
            quantidade
        )

        cursor.execute(sql_log, dados_log)


        
        #-----------------------------------------------------

        #-----------------------------------------------------
        # Salva na tabela inventario
        #-----------------------------------------------------

        cursor.execute("""
            SELECT COALESCE(MAX(inv_numero::INTEGER), 0) + 1 AS novo_numero
            FROM inventario
            WHERE inv_numero ~ '^[0-9]+$'
        """) 

       

        resultado = cursor.fetchone()

        novo_numero = str(resultado["novo_numero"])    


        if quantidade ==0:
           tipo = "Z"
           qtde_entrada_saida = 0

        elif quantidade < qtdeAnterior:
           tipo = "S"
           qtde_entrada_saida = qtdeAnterior - quantidade
           
        elif quantidade > qtdeAnterior:
            if qtdeAnterior <0:
               tipo = "E"
               qtde_entrada_saida = quantidade- abs(qtdeAnterior )
            else:
               tipo = "E"
               qtde_entrada_saida = quantidade+ qtdeAnterior 
            
            

           



          
         

        
        sql_inv = """
            INSERT INTO inventario(
                inv_codproduto,
                inv_data,
                inv_inventario,
                inv_login,
                inv_numero,
                inv_hora,
                inv_obs,
                inv_qtde,
                inv_tipo,
                inv_qtde_entrada_saida
            )
            VALUES (
                %s, 
                CURRENT_DATE,
                %s, 
                %s, 
                %s,
                CURRENT_TIME,
                %s,
                %s,
                %s,
                %s
                
                
            )
        """
          
        dados_inv = (
            codigo_produto,
            quantidade,
            'API',
            novo_numero,
            'API',
            qtdeAnterior,
            tipo,
            qtde_entrada_saida
        )

        cursor.execute(sql_inv, dados_inv)
        
        #-----------------------------------------------------
        #-----------------------------------------------------



        conn.commit()

        proximo_num = row["est_qtde"]

        return {
            "mensagem": "estoque atualizado com sucesso",
            "nova_qtde": proximo_num
        }

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar: {str(e)}"
        )

    finally:

        cursor.close()
        release_conexao(conn)

      
