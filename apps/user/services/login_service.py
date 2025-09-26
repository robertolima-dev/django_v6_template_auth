from django.contrib.auth import authenticate


class LoginService:
    def login(self, request, email: str, password: str):
        if not email or not password:
            raise Exception("Email e senha são obrigatórios.")

        user = authenticate(request, username=email, password=password)
        if not user:
            raise Exception("Credenciais inválidas.")

        if not getattr(user, "is_active", True):
            raise Exception("Usuário inativo.")

        return user