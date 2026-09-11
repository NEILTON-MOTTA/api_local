from fastapi import FastAPI
from routes import cliente              # importa cliente.py
from routes import valida_usuario       # importa valida_usuario.py
from routes import numerador_clientes   # importa valida_usuario.py
from routes import produto              # importa produto.py
from routes import adm                  # importa adm.py
from routes import parceiro

app = FastAPI()

app.include_router(cliente.router)
app.include_router(valida_usuario.router)
app.include_router(numerador_clientes.router)
app.include_router(produto.router)
app.include_router(adm.router)

# ---------------------------------------------------------
# API EXTERNA / PARCEIRO
# ---------------------------------------------------------
parceiro_app = FastAPI(
    title="API PARCEIRO "
)

parceiro_app.include_router(parceiro.router)
