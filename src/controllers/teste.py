
from datetime import datetime, timedelta, timezone
import hashlib

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError

app = FastAPI(title="API - Doenças Raras")

# Configurações do token
CHAVE_SECRETA = "chave_secreta_projeto_faculdade"
ALGORITMO = "HS256"
TEMPO_TOKEN = 30

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Armazenamento temporário dos usuários
usuarios = {}


# Dados recebidos no cadastro
class Usuario(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class AtualizarNome(BaseModel):
    nome: str


class UsuarioPublico(BaseModel):
    id: str
    nome: str
    email: EmailStr


def gerar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def gerar_token(email):
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=TEMPO_TOKEN
    )

    dados = {"sub": email, "exp": expiracao}

    return jwt.encode(
        dados, CHAVE_SECRETA, algorithm=ALGORITMO
    )


def usuario_logado(token: str = Depends(oauth2)):
    try:
        dados = jwt.decode(
            token, CHAVE_SECRETA, algorithms=[ALGORITMO]
        )

        email = dados.get("sub")

        if not email or email not in usuarios:
            raise HTTPException(
                status_code=401,
                detail="Usuário não autenticado"
            )

        return usuarios[email]

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )


@app.post("/usuarios/", response_model=UsuarioPublico)
def cadastrar(usuario: Usuario):
    if usuario.email in usuarios:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    novo_usuario = {
        "id": str(len(usuarios) + 1),
        "nome": usuario.nome,
        "email": usuario.email,
        "senha_hash": gerar_hash(usuario.senha)
    }

    usuarios[usuario.email] = novo_usuario

    return novo_usuario


@app.post("/login/")
def fazer_login(
    dados: OAuth2PasswordRequestForm = Depends()
):
    usuario = usuarios.get(dados.username)

    if not usuario or usuario["senha_hash"] != gerar_hash(
        dados.password
    ):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos"
        )

    token = gerar_token(usuario["email"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/usuarios/me", response_model=UsuarioPublico)
def meu_perfil(usuario=Depends(usuario_logado)):
    return usuario


@app.put("/usuarios/me", response_model=UsuarioPublico)
def atualizar_perfil(
    dados: AtualizarNome,
    usuario=Depends(usuario_logado)
):
    usuario["nome"] = dados.nome
    return usuario