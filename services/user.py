import re

from fastapi.responses import RedirectResponse

from tools.session_error import set_session_error
from tools.password import Password


class User:
    def __init__(self, repo):
        self.repo = repo
        self.password = Password()


    async def create(self, name: str, email: str, password: str) -> RedirectResponse:
        """Cria um novo usuário."""
        response = RedirectResponse(url="/create", status_code=302)
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
        