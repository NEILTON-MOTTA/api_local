import logging
import os

from dotenv import load_dotenv
from psycopg2 import extensions
from psycopg2.pool import ThreadedConnectionPool

load_dotenv()
logger = logging.getLogger(__name__)

# Mantem os limites originais dos dois pools.
connection_pool = ThreadedConnectionPool(
    1, 10,
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    connect_timeout=10,
)

connection_pool_imagem = ThreadedConnectionPool(
    1, 5,
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database='imagens',
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    connect_timeout=10,
)


def _obter_conexao(pool, nome):
    for tentativa in range(2):
        conn = pool.getconn()  # PoolError (esgotado) deve aparecer no log da rota.
        try:
            if conn.closed:
                raise RuntimeError('Conexao ja fechada')

            # Nao entregar uma transacao antiga para a proxima requisicao.
            if conn.get_transaction_status() != extensions.TRANSACTION_STATUS_IDLE:
                conn.rollback()

            with conn.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            conn.rollback()  # SELECT inicia transacao se autocommit=False.
            return conn
        except Exception:
            logger.exception(
                'Falha ao validar conexao do banco %s (tentativa %s/2)',
                nome, tentativa + 1,
            )
            try:
                pool.putconn(conn, close=True)
            except Exception:
                logger.exception('Falha ao descartar conexao do banco %s', nome)
            if tentativa == 1:
                raise


def _devolver_conexao(pool, conn, nome):
    if conn is None:
        return
    try:
        if conn.closed:
            pool.putconn(conn, close=True)
            return
        # Impede que transacoes abertas/abortadas passem para outra requisicao.
        if conn.get_transaction_status() != extensions.TRANSACTION_STATUS_IDLE:
            conn.rollback()
        pool.putconn(conn)
    except Exception:
        logger.exception('Falha ao devolver conexao do banco %s', nome)
        # Tenta retirar do pool a conexao defeituosa.
        try:
            pool.putconn(conn, close=True)
        except Exception:
            logger.exception('Falha ao descartar conexao do banco %s', nome)
        raise


def get_conexao():
    return _obter_conexao(connection_pool, 'principal')


def release_conexao(conn):
    _devolver_conexao(connection_pool, conn, 'principal')


def get_conexao_imagem():
    return _obter_conexao(connection_pool_imagem, 'imagens')


def release_conexao_imagem(conn):
    _devolver_conexao(connection_pool_imagem, conn, 'imagens')
