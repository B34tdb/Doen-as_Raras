
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
import pymssql as sql 
import mysql.connector 

conexao = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="Sc4rfac3_023412",
    database="DOENCAS_RARAS"
)

cursor = conexao.cursor()
cursor.execute("SELECT DATABASE()")
resultado = cursor.fetchone()




app = FastAPI(title="API - Doenças Raras")

# Configurações do token
CHAVE_SECRETA = "chave_secreta_projeto_faculdade"
ALGORITMO = "HS256"
TEMPO_TOKEN = 30

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Armazenamento temporário dos usuários
usuario={}


# Dados recebidos no cadastro
class Usuario(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cpf: str
    crm: Optional[str] = None


class AtualizarNome(BaseModel):
    nome: str


class UsuarioPublico(BaseModel):
    id: str
    nome: str
    email: EmailStr
def usuario_publico(linha):
    return {
        "id": linha["idusuario"],
        "nome": linha["nome"],
        "email": linha["email"],
    }


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

        if not email or email not in usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuário não autenticado"
            )

        return usuario[email]

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )


@app.post("/usuario", response_model=UsuarioPublico)
def cadastrar(dados: Usuario):
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT idusuario FROM usuario WHERE email = %s",
        (dados.email,)
    )
    if cursor.fetchone():
        cursor.close()
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    cursor.execute(
        "INSERT INTO usuario (nome, email, senha, cpf, crm) VALUES (%s, %s, %s, %s, %s)",
        (dados.nome, dados.email, gerar_hash(dados.senha), dados.cpf, dados.crm)
    )
    conexao.commit()

    novo_id = cursor.lastrowid
    cursor.close()

    return {
        "id": str(novo_id),
        "nome": dados.nome,
        "email": dados.email
    }

# @app.post("/login/")
# def fazer_login(
#     dados: OAuth2PasswordRequestForm = Depends()
# ):
#     usuario = usuario.get(dados.username)

#     if not usuario or usuario["senha_hash"] != gerar_hash(
#         dados.password
#     ):
#         raise HTTPException(
#             status_code=401,
#             detail="E-mail ou senha incorretos"
#         )

#     token = gerar_token(usuario["email"])

#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }
@app.post("/login/")
def fazer_login(
    dados: OAuth2PasswordRequestForm = Depends()
):
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT email, senha
        FROM usuario
        WHERE email = %s
        """,
        ( dados.username,)
    )

    usuario_db = cursor.fetchone()

    cursor.close()

    if not usuario_db:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou usuário incorretos"
        )

    if usuario_db["senha"] != gerar_hash(dados.password):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos"
        )

    token = gerar_token(usuario_db["email"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/usuario/", response_model=UsuarioPublico)
def meu_perfil(usuario=Depends(usuario_logado)):
    return usuario





@app.put("/usuario/{id_usuario}")
def atualizar_perfil(id_usuario: int, dados: AtualizarNome):
  
    cursor = conexao.cursor()
 
    cursor.execute(
        "UPDATE usuario SET nome = %s," , " update usuario SET email =%s," " WHERE idusuario = %s",
        (dados.nome, id_usuario)
    )
 
    conexao.commit()
 
    if cursor.rowcount == 0:
        cursor.close()
        conexao.close()
 
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
 
    cursor.close()
    conexao.close()
 
    return {
        "mensagem": "Usuário atualizado com sucesso",
        "idusuario": id_usuario,
        "nome": dados.nome
    }
 


@app.delete("/usuario/{id_usuario}")
def deletar_usuario(id_usuario: int):
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM usuario WHERE idusuario = %s",
        (id_usuario,)
    )

    conexao.commit()

    if cursor.rowcount == 0:
    
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )


    return {
        "mensagem": "Usuário deletado com sucesso",
        "idusuario": id_usuario
    }