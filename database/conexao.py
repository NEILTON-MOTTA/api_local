import os
from dotenv import load_dotenv
from psycopg2.pool import ThreadedConnectionPool

# Carrega o arquivo .env
load_dotenv()

# Cria o pool
connection_pool = ThreadedConnectionPool(
    1,
    10,
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Pega conexão
def get_conexao():
    return connection_pool.getconn()

# Devolve conexão
def release_conexao(conn):
    connection_pool.putconn(conn)
