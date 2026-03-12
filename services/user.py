import re
import hashlib

from fastapi.responses import RedirectResponse

from config.config import MAX_TOKENS_PER_USER
from tools.session_error import set_session_error
from tools.password import Password


class User:
    def __init__(self, repo):
        self.repo = repo
        self.password = Password()


    async def create(self, name: str, email: str, password: str) -> RedirectResponse:
        """Cria um novo usuário."""
        response = RedirectResponse(url="/user/create", status_code=302)
        validate_data = await self.validate_create_user_data(name, email, password)
        if validate_data["error"]:
            set_session_error(response, ";".join(validate_data["errors"]))
            return response

        existing_user = await self.repo.get_user_by_email(email)
        if existing_user:
            set_session_error(response, "Email já cadastrado")
            return response

        try:
            password_hash = self.password.hash(password)
            await self.repo.create_user(name, email, password_hash)
        except Exception:
            set_session_error(response, "Erro ao criar usuário")
            return response
        
        response.headers['location'] = "/login"
        return response


    async def validate_create_user_data(self, name: str, email: str, password: str) -> dict:
        """Valida os dados de criação de usuário."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        errors = []
        if not name:
            errors.append("O nome é obrigatório.")
        elif len(name) < 3:
            errors.append("O nome deve ter pelo menos 3 caracteres.")
        elif len(name.split()) < 2:
            errors.append("O nome deve conter pelo menos um sobrenome.")

        if not email:
            errors.append("O email é obrigatório.")
        elif not bool(re.match(email_pattern, email)):
            errors.append("O email deve ser válido.")

        if not password:
            errors.append("A senha é obrigatória.")
        elif len(password) < 6:
            errors.append("A senha deve ter pelo menos 6 caracteres.")
        
        return_data = {
            "error": len(errors) > 0,
            "errors": errors
        }
        return return_data
    

    async def get_tokens(self, user_id: int) -> list:
        """Retorna os tokens do usuário."""
        tokens = await self.repo.get_tokens_by_user_id(user_id)
        return tokens
    
    
    async def create_token(self, user_id: int, name: str) -> RedirectResponse:
        response = RedirectResponse(url="/user/token/create", status_code=302)
        validate_data = self.validate_create_token_data(name)
        if validate_data["error"]:
            set_session_error(response, ";".join(validate_data["errors"]))
            return response

        existing_tokens = await self.repo.get_tokens_by_user_id(user_id)
        if len(existing_tokens) >= MAX_TOKENS_PER_USER:
            set_session_error(response, "Limite de tokens por usuário atingido.")
            return response

        try:
            token_value = hashlib.sha256(f"{user_id}:{name}".encode()).hexdigest()
            await self.repo.create_token(user_id, name, token_value)
        except Exception:
            set_session_error(response, "Erro ao criar token")
            return response

        response.headers['location'] = "/user/token"
        return response


    def validate_create_token_data(self, name: str) -> dict:
        errors = []
        if not name:
            errors.append("O nome do token é obrigatório.")
        elif len(name) < 3:
            errors.append("O nome do token deve ter pelo menos 3 caracteres.")
        elif len(name) > 50:
            errors.append("O nome do token deve conter no máximo 50 caracteres.")
        
        return_data = {
            "error": len(errors) > 0,
            "errors": errors
        }
        return return_data


    async def delete_token(self, user_id: int, token_id: int) -> RedirectResponse:
        response = RedirectResponse(url="/user/token", status_code=302)
        try:
            await self.repo.delete_token(user_id,token_id)
        except Exception:
            set_session_error(response, "Erro ao deletar token")
            return response

        return response