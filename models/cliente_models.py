from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re
from datetime import datetime
# Imports de FastAPI aqui são desnecessários no arquivo de modelos, 
# mas não quebram nada. Pode deixar se preferir.
# from fastapi import APIRouter, Body, HTTPException

# -----------------------------------------------------------------
# Base (mantida aqui só para futura expansão; por enquanto: pass)
# -----------------------------------------------------------------
class ClienteBase(BaseModel):
    pass

# --------------------------------------
# Modelo de entrada (POST /cliente)
# --------------------------------------
class ClienteIn(BaseModel):
    # Obrigatórios
    cli_codigo: str
    cli_nome: str
    cli_cnpj: str

    # Opcionais
    cli_fantasia: Optional[str] = None
    cli_tipo: Optional[str] = None
    cli_regimetributario: Optional[int] = None
    cli_inscricao: Optional[str] = None
    cli_datacad: Optional[str] = None      # string DD/MM/YYYY
    cli_ativo: Optional[int] = None
    cli_datanasc: Optional[str] = None     # string DD/MM/YYYY
    cli_codmunicipio: Optional[str] = None
    cli_tipologradouro: Optional[str] = None
    cli_logradouro: Optional[str] = None
    cli_numero: Optional[str] = None
    cli_complemento: Optional[str] = None
    cli_cep: Optional[str] = None
    cli_uf: Optional[str] = None
    cli_cidade: Optional[str] = None
    cli_bairro: Optional[str] = None
    cli_ponto_ref: Optional[str] = None
    cli_telefone1: Optional[str] = None
    cli_telefone2: Optional[str] = None
    cli_telefone3: Optional[str] = None
    cli_telefone4: Optional[str] = None
    cli_contato: Optional[str] = None
    cli_email: Optional[EmailStr] = None
    cli_obs: Optional[str] = None
    cli_desativar_sistema: Optional[bool] = None

    # --- Normalizações e validações ---

    # Remove não dígitos e garante 14 para CNPJ (mantido como você fez)
    @validator("cli_cnpj")
    def valida_cnpj(cls, v: str) -> str:
        d = re.sub(r"\D", "", v or "")
        if len(d) not in (11, 14):
            raise ValueError("CNPJ deve ter 11 (CPF) ou 14 (CNPJ) dígitos")
        return d
   
    # CEP só dígitos
    @validator("cli_cep", pre=True)
    def normaliza_cep(cls, v):
        if v is None:
            return v
        v = re.sub(r"\D", "", str(v))
        return v

    # Telefones só dígitos
    @validator("cli_telefone1", "cli_telefone2", "cli_telefone3", "cli_telefone4", pre=True)
    def normaliza_fones(cls, v):
        if v is None:
            return v
        v = re.sub(r"\D", "", str(v))
        return v

    # Datas DD/MM/YYYY válidas (sem converter)
    @validator("cli_datacad", "cli_datanasc")
    def valida_data_brasileira(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Data deve estar no formato DD/MM/YYYY e ser válida")
        return v

    # UF em maiúsculas com 2 letras (se informado)
    @validator("cli_uf", pre=True)
    def valida_uf(cls, v):
        if v is None:
            return v
        v = str(v).strip().upper()
        if v and len(v) != 2:
            raise ValueError("UF deve conter 2 letras")
        return v

    # IBGE 7 dígitos (se informado)
    @validator("cli_codmunicipio", pre=True)
    def valida_codmunicipio(cls, v):
        if v is None:
            return v
        v = re.sub(r"\D", "", str(v))
        return v

    # Higieniza espaços
    @validator(
        "cli_codigo", "cli_nome", "cli_fantasia", "cli_tipologradouro",
        "cli_logradouro", "cli_numero", "cli_complemento", "cli_bairro",
        "cli_cidade", "cli_ponto_ref", "cli_contato", "cli_obs",
        pre=True
    )
    def strip_textos(cls, v):
        if v is None:
            return v
        return str(v).strip()

    # E-mail minúsculo
    @validator("cli_email", pre=True)
    def normaliza_email(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()


# --------------------------------------
# Modelo de entrada (PUT /cliente)
# --------------------------------------
class ClienteUpdate(BaseModel):
    # ADIÇÃO mínima para combinar com seu validador:
    cli_cnpj: Optional[str] = None  # <- agora o validador abaixo tem o campo

    cli_fantasia: Optional[str] = None
    cli_tipo: Optional[str] = None
    cli_regimetributario: Optional[int] = None
    cli_inscricao: Optional[str] = None
    cli_datacad: Optional[str] = None      # string DD/MM/YYYY
    cli_ativo: Optional[int] = None
    cli_datanasc: Optional[str] = None     # string DD/MM/YYYY
    cli_codmunicipio: Optional[str] = None
    cli_tipologradouro: Optional[str] = None
    cli_logradouro: Optional[str] = None
    cli_numero: Optional[str] = None
    cli_complemento: Optional[str] = None
    cli_cep: Optional[str] = None
    cli_uf: Optional[str] = None
    cli_cidade: Optional[str] = None
    cli_bairro: Optional[str] = None
    cli_ponto_ref: Optional[str] = None
    cli_telefone1: Optional[str] = None
    cli_telefone2: Optional[str] = None
    cli_telefone3: Optional[str] = None
    cli_telefone4: Optional[str] = None
    cli_contato: Optional[str] = None
    cli_email: Optional[EmailStr] = None
    cli_obs: Optional[str] = None
    cli_desativar_sistema: Optional[bool] = None

    @validator("cli_cnpj")
    def valida_cnpj_ou_cpf(cls, v):
        if v is None:
            return v
        dig = re.sub(r"\D", "", v)
        if len(dig) not in (11, 14):
            raise ValueError("cli_cnpj deve ter 11 (CPF) ou 14 (CNPJ) dígitos.")
        return dig

    @validator("cli_datacad", "cli_datanasc")
    def valida_data_brasileira(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Data deve estar no formato DD/MM/YYYY e ser válida.")
        return v

    @validator("cli_telefone1", "cli_telefone2", pre=True)
    def normaliza_telefone(cls, v):
        if v is None:
            return v
        return re.sub(r"\D", "", v)
