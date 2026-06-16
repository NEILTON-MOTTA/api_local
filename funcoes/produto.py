
from database.conexao import get_conexao, release_conexao


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
