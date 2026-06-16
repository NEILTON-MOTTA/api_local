# routes/cliente.py
from fastapi import APIRouter, Depends, HTTPException,Body, Security, status,Query
from fastapi.security.api_key import APIKeyHeader
from database.conexao import get_conexao, release_conexao
from psycopg2.extras import RealDictCursor
import re
from models.cliente_models import ClienteIn
from models.cliente_models import ClienteUpdate
from typing import Dict, Any








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
# --- Rota 1: Buscar cliente por codigo ---
# -----------------------------------------
@router.get("/cliente_id/{cli_codigo}", dependencies=[Depends(validar_api_key)])
def get_cliente(cli_codigo: str):
    conn = get_conexao()
    cursor = conn.cursor()
    try:
        cursor.execute("""
             SELECT  cli_codigo,cli_nome,cli_fantasia,cli_tipo,cli_regimetributario,cli_cnpj,cli_inscricao,cli_datacad,
        cli_ativo,cli_datanasc,cli_codmunicipio,cli_tipologradouro,cli_logradouro,cli_numero,cli_complemento,
        cli_cep,cli_uf,cli_cidade,cli_bairro,cli_ponto_ref,
        cli_telefone1,cli_telefone2,cli_telefone3,cli_telefone4,cli_contato,cli_email,cli_obs,cli_desativar_sistema
        FROM clientes 
        WHERE cli_codigo = %s
        """, (cli_codigo,))
        cliente = cursor.fetchone()
    finally:
        cursor.close()
        release_conexao(conn)

    if cliente:
        return {
                 "__codigo": cliente[0],
                 "__nome": cliente[1],
                 "__fantasia": cliente[2],
                 "__tipo": cliente[3],
                 "__regimetributario": cliente[4],
                 "__cnpj": cliente[5],
                 "__inscricao": cliente[6],
                 "__datacad": cliente[7],
                 "__ativo": cliente[8],
                 "__datanasc": cliente[9],
                 "__codmunicipio": cliente[10],
                 "__tipologradouro": cliente[11],
                 "__logradouro": cliente[12],
                 "__numero": cliente[13],
                 "__complemento": cliente[14],
                 "__cep": cliente[15],
                 "__uf": cliente[16],
                 "__cidade": cliente[17],
                 "__bairro": cliente[18],
                 "__ponto_ref": cliente[19],
                 "__telefone1": cliente[20],
                 "__telefone2": cliente[21],
                 "__telefone3": cliente[22],
                 "__telefone4": cliente[23],
                 "__contato": cliente[24],
                 "__email": cliente[25],
                 "__obs": cliente[26],
                 "__desativar_sistema": cliente[27],
                 "__retorno":"1"
        }
    else:
        return {
            "cli_codigo": cli_codigo,
            "mensagem": "cliente não encontrado",
            "__retorno":"0"
        }

# ---------------------------------------
# --------------FIM----------------------
# ---------------------------------------




# ---------------------------------------
# --- Rota 2: Buscar cliente por CNPJ ---
# ---------------------------------------
@router.get("/cliente_cnpj/{cnpj}")
def get_cliente_por_cnpj(cnpj: str, cred = Depends(validar_api_key)):
    cnpj_cliente = re.sub(r"\D", "", cnpj or "")
    if len(cnpj_cliente) != 14:
        raise HTTPException(status_code=400, detail="CNPJ inválido (use 14 dígitos).")

    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
        SELECT  cli_codigo,cli_nome,cli_fantasia,cli_tipo,cli_regimetributario,cli_cnpj,cli_inscricao,cli_datacad,
        cli_ativo,cli_datanasc,cli_codmunicipio,cli_tipologradouro,cli_logradouro,cli_numero,cli_complemento,
        cli_cep,cli_uf,cli_cidade,cli_bairro,cli_ponto_ref,
        cli_telefone1,cli_telefone2,cli_telefone3,cli_telefone4,cli_contato,cli_email,cli_obs,cli_desativar_sistema
        FROM clientes 
            WHERE cli_cnpj = %s
            LIMIT 1
        """, (cnpj_cliente,))
        cliente = cur.fetchone()
    finally:
        cur.close()
        release_conexao(conn)

    if cliente:
        return {
                 "__codigo": cliente["cli_codigo"],
                 "__nome": cliente["cli_nome"],
                 "__fantasia": cliente["cli_fantasia"],
                 "__tipo": cliente["cli_tipo"],
                 "__regimetributario": cliente["cli_regimetributario"],
                 "__cnpj": cliente["cli_cnpj"],
                 "__inscricao": cliente["cli_inscricao"],
                 "__datacad": cliente["cli_datacad"],
                 "__ativo": cliente["cli_ativo"],
                 "__datanasc": cliente["cli_datanasc"],
                 "__codmunicipio": cliente["cli_codmunicipio"],
                 "__tipologradouro": cliente["cli_tipologradouro"],
                 "__logradouro": cliente["cli_logradouro"],
                 "__numero": cliente["cli_numero"],
                 "__complemento": cliente["cli_complemento"],
                 "__cep": cliente["cli_cep"],
                 "__uf": cliente["cli_uf"],
                 "__cidade": cliente["cli_cidade"],
                 "__bairro": cliente["cli_bairro"],
                 "__ponto_ref": cliente["cli_ponto_ref"],
                 "__telefone1": cliente["cli_telefone1"],
                 "__telefone2": cliente["cli_telefone2"],
                 "__telefone3": cliente["cli_telefone3"],
                 "__telefone4": cliente["cli_telefone4"],
                 "__contato": cliente["cli_contato"],
                 "__email": cliente["cli_email"],
                 "__obs": cliente["cli_obs"],
                 "__desativar_sistema":  cliente["cli_desativar_sistema"],
                 "__retorno":"1"
        }

    else:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    



# ---------------------------------------
# --------------FIM----------------------
# ---------------------------------------
  
# --- Rota 3: Buscar cliente por Nome ---  

@router.get("/cliente_nome/{nome}")
def get_cliente_por_nome(nome: str, limit: int = Query(50, ge=1, le=200),cred = Depends(validar_api_key)):
    """
    Busca clientes por nome (parcial), sem diferenciar maiúsculas/minúsculas.
    Ex.: /cliente_nome/joao?limit=20
    """
    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  cli_codigo,cli_nome,cli_fantasia,cli_tipo,cli_regimetributario,cli_cnpj,cli_inscricao,cli_datacad,
        cli_ativo,cli_datanasc,cli_codmunicipio,cli_tipologradouro,cli_logradouro,cli_numero,cli_complemento,
        cli_cep,cli_uf,cli_cidade,cli_bairro,cli_ponto_ref,
        cli_telefone1,cli_telefone2,cli_telefone3,cli_telefone4,cli_contato,cli_email,cli_obs,cli_desativar_sistema
        FROM clientes 
        WHERE cli_nome ILIKE %s
        ORDER BY cli_nome ASC
        LIMIT %s
        """,
        (f"%{nome}%", limit)
    )
    rows = cursor.fetchall()

    cursor.close()
    release_conexao(conn)

    # Mantendo o estilo de retorno com índices (tuplas)
    resultados = [
        {
                 "__codigo": r[0],
                 "__nome": r[1],
                 "__fantasia": r[2],
                 "__tipo": r[3],
                 "__regimetributario": r[4],
                 "__cnpj": r[5],
                 "__inscricao": r[6],
                 "__datacad": r[7],
                 "__ativo": r[8],
                 "__datanasc": r[9],
                 "__codmunicipio": r[10],
                 "__tipologradouro": r[11],
                 "__logradouro": r[12],
                 "__numero": r[13],
                 "__complemento": r[14],
                 "__cep": r[15],
                 "__uf": r[16],
                 "__cidade": r[17],
                 "__bairro": r[18],
                 "__ponto_ref": r[19],
                 "__telefone1": r[20],
                 "__telefone2": r[21],
                 "__telefone3": r[22],
                 "__telefone4": r[23],
                 "__contato": r[24],
                 "__email": r[25],
                 "__obs": r[26],
                 "__desativar_sistema": r[27],
                 "__retorno":"1"
                 
        }
        for r in rows
    ]

    return {
        "count": len(resultados),
        "items": resultados
    }






# ------------------------------------------
# --- Rota 4: Buscar por Telefone1  -------
# ------------------------------------------

@router.get("/cliente_telefone1/{telefone1}")
def get_cliente_por_telefone1(telefone1: str, limit: int = Query(50, ge=1, le=200),cred = Depends(validar_api_key)):
    """
    Busca clientes por telefone1 (parcial), sem diferenciar maiúsculas/minúsculas.
    Ex.: /cliente_telefone1/964729158?limit=20
    """

    if not  telefone1:
        raise HTTPException(status_code=400, detail="telefone1 invalido.")

    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  cli_codigo,cli_nome,cli_fantasia,cli_tipo,cli_regimetributario,cli_cnpj,cli_inscricao,cli_datacad,
        cli_ativo,cli_datanasc,cli_codmunicipio,cli_tipologradouro,cli_logradouro,cli_numero,cli_complemento,
        cli_cep,cli_uf,cli_cidade,cli_bairro,cli_ponto_ref,
        cli_telefone1,cli_telefone2,cli_telefone3,cli_telefone4,cli_contato,cli_email,cli_obs,cli_desativar_sistema
        FROM clientes 
        WHERE cli_telefone1 ILIKE %s
        ORDER BY cli_nome ASC
        LIMIT %s
        """,
        (f"%{telefone1}%", limit)
    )
    rows = cursor.fetchall()

    cursor.close()
    release_conexao(conn)

    # Mantendo o estilo de retorno com índices (tuplas)
    resultados = [
        {
                 "__codigo": r[0],
                 "__nome": r[1],
                 "__fantasia": r[2],
                 "__tipo": r[3],
                 "__regimetributario": r[4],
                 "__cnpj": r[5],
                 "__inscricao": r[6],
                 "__datacad": r[7],
                 "__ativo": r[8],
                 "__datanasc": r[9],
                 "__codmunicipio": r[10],
                 "__tipologradouro": r[11],
                 "__logradouro": r[12],
                 "__numero": r[13],
                 "__complemento": r[14],
                 "__cep": r[15],
                 "__uf": r[16],
                 "__cidade": r[17],
                 "__bairro": r[18],
                 "__ponto_ref": r[19],
                 "__telefone1": r[20],
                 "__telefone2": r[21],
                 "__telefone3": r[22],
                 "__telefone4": r[23],
                 "__contato": r[24],
                 "__email": r[25],
                 "__obs": r[26],
                 "__detativar_sistema": r[27],
                 "__retorno":"1"
        }
        for r in rows
    ]

    return {
        "count": len(resultados),
        "items": resultados
    }






# ------------------------------------------
# --- Rota 5: Buscar por logradouro  -------
# ------------------------------------------

@router.get("/cliente_logradouro/{logradouro}")
def get_cliente_por_logradouro(logradouro: str, limit: int = Query(50, ge=1, le=200),cred = Depends(validar_api_key)):
    """
    Busca clientes por logradouro (parcial), sem diferenciar maiúsculas/minúsculas.
    Ex.: /cliente_logradouro/sabara?limit=20
    """

    if not  logradouro:
        raise HTTPException(status_code=400, detail="logradouro invalido.")

    conn = get_conexao()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT  cli_codigo,cli_nome,cli_fantasia,cli_tipo,cli_regimetributario,cli_cnpj,cli_inscricao,cli_datacad,
        cli_ativo,cli_datanasc,cli_codmunicipio,cli_tipologradouro,cli_logradouro,cli_numero,cli_complemento,
        cli_cep,cli_uf,cli_cidade,cli_bairro,cli_ponto_ref,
        cli_telefone1,cli_telefone2,cli_telefone3,cli_telefone4,cli_contato,cli_email,cli_obs,cli_desativar_sistema
        FROM clientes 
        WHERE cli_logradouro ILIKE %s
        ORDER BY cli_nome ASC
        LIMIT %s
        """,
        (f"%{logradouro}%", limit)
    )
    rows = cursor.fetchall()

    cursor.close()
    release_conexao(conn)

    # Mantendo o estilo de retorno com índices (tuplas)
    resultados = [
        {
                 "__codigo": r[0],
                 "__nome": r[1],
                 "__fantasia": r[2],
                 "__tipo": r[3],
                 "__regimetributario": r[4],
                 "__cnpj": r[5],
                 "__inscricao": r[6],
                 "__datacad": r[7],
                 "__ativo": r[8],
                 "__datanasc": r[9],
                 "__codmunicipio": r[10],
                 "__tipologradouro": r[11],
                 "__logradouro": r[12],
                 "__numero": r[13],
                 "__complemento": r[14],
                 "__cep": r[15],
                 "__uf": r[16],
                 "__cidade": r[17],
                 "__bairro": r[18],
                 "__ponto_ref": r[19],
                 "__telefone1": r[20],
                 "__telefone2": r[21],
                 "__telefone3": r[22],
                 "__telefone4": r[23],
                 "__contato": r[24],
                 "__email": r[25],
                 "__obs": r[26],
                 "__desativar_sistema": r[27],
                 "__retorno":"1",
                 
        }
        for r in rows
    ]

    return {
        "count": len(resultados),
        "items": resultados
    }


#--------------------------------------------------------------------------
#  6 Rota do Insert
#--------------------------------------------------------------------------
@router.post("/cliente", dependencies=[Depends(validar_api_key)])
def inserir_cliente(payload: ClienteIn = Body(...)):
    dados = payload.dict(exclude_none=True)

    # checa obrigatórios
    obrigatorios = ["cli_codigo", "cli_nome", "cli_cnpj"]
    faltando = [c for c in obrigatorios if c not in dados or not dados[c]]
    if faltando:
        raise HTTPException(status_code=422, detail=f"Campos obrigatórios ausentes: {', '.join(faltando)}")

    # Colunas que são DATE no PostgreSQL
    campos_data = {"cli_datacad", "cli_datanasc"}

    colunas = []
    valores_expr = []
    for k in dados.keys():
        colunas.append(k)
        if k in campos_data:
            valores_expr.append(f"to_date(%({k})s, 'DD/MM/YYYY')")
        else:
            valores_expr.append(f"%({k})s")

    sql = f"""
        INSERT INTO clientes ({', '.join(colunas)})
        VALUES ({', '.join(valores_expr)})
    """

    conn = get_conexao()
    cur = conn.cursor()
    try:
        cur.execute(sql, dados)
        conn.commit()
        return {"mensagem": "Cliente inserido com sucesso", "__retorno": "1"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao inserir cliente: {str(e)}")
    finally:
        cur.close()
        release_conexao(conn)







#--------------------------------------------------------------------------
#  Rota de PATCH — Atualiza somente campos enviados no Body
#--------------------------------------------------------------------------

# from routes.seguranca import validar_api_key  # ajuste se necessário

router = APIRouter()

@router.patch("/cliente/{cli_codigo}", dependencies=[Depends(validar_api_key)])
def atualizar_cliente_parcial(cli_codigo: str, payload: Dict[str, Any] = Body(...)):
    dados: Dict[str, Any] = payload or {}

    # campos DATE no PostgreSQL
    campos_data = {"cli_datacad", "cli_datanasc"}

    # monta pares coluna=valor
    set_clauses = []
    params: Dict[str, Any] = {}

    for k, v in dados.items():
        # opcional: string vazia -> NULL
        if isinstance(v, str) and v.strip() == "":
            v = None

        if k in campos_data:
            if v is None:
                set_clauses.append(f"{k} = NULL")
            else:
                set_clauses.append(f"{k} = to_date(%({k})s, 'DD/MM/YYYY')")
                params[k] = v
        else:
            set_clauses.append(f"{k} = %({k})s")
            params[k] = v

    if not set_clauses:
        raise HTTPException(status_code=400, detail="Nenhum campo enviado para atualização.")

    sql = f"""
        UPDATE clientes
           SET {', '.join(set_clauses)}
         WHERE cli_codigo = %(cli_codigo)s
     RETURNING *;
    """
    # agora sim: adiciona o path param ao dicionário de parâmetros
    params["cli_codigo"] = cli_codigo

    conn = get_conexao()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # debug opcional
        try:
            sql_debug = cur.mogrify(sql, params)
            print("---- SQL GERADA (PATCH) ----")
            print(sql_debug.decode() if isinstance(sql_debug, bytes) else sql_debug)
            print("----------------------------")
        except Exception as dbg_err:
            print("⚠️ Erro ao gerar SQL para debug (mogrify):", dbg_err)

        cur.execute(sql, params)

        if cur.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")

        row = cur.fetchone()
        conn.commit()
        return {"mensagem": "Cliente Alterado com sucesso", "cliente": row, "__retorno": "1"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar cliente: {e}")
    finally:
        try:
            cur.close()
        except Exception:
            pass
        release_conexao(conn)
