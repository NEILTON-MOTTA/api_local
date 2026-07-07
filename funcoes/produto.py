
from database.conexao import get_conexao, release_conexao,get_conexao_imagem, release_conexao_imagem


def buscar_quantidade_produto(codigo: str):
    conn = get_conexao()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT est_qtde
            FROM estoque
            WHERE est_codigo = %s
        """, (codigo,))

        resultado = cursor.fetchone()

        if resultado is None:
            return None

        return resultado[0]

    finally:
        cursor.close()
        release_conexao(conn)


def buscar_quantidade_fotos(codigo: str):
    conn = get_conexao_imagem()
    cursor = conn.cursor()

    try:
       cursor.execute("""
          SELECT count(fot_numero)  as xtot
          from fotos_produtos
          WHERE fot_codproduto = %s
       """, (codigo,))

       resultado = cursor.fetchone()

       if resultado is None:
           return None

       return resultado[0]

    finally:
        cursor.close()
        release_conexao_imagem(conn)


#-----------------------------------------------------------
# conta Produtos por descricao
#-----------------------------------------------------------
def contar_produtos_por_descricao(descricao: str):
    conn = get_conexao()
    cursor = conn.cursor()

    try:
       cursor.execute("""
         SELECT COUNT(*)
         FROM estoque
         WHERE est_descricao ILIKE %s
       """, (f"{descricao}%",))

       resultado = cursor.fetchone()

       if resultado is None:
           return None

       return resultado[0]

    finally:
        cursor.close()
        release_conexao(conn)

