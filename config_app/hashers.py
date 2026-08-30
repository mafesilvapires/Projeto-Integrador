from django.contrib.auth.hashers import PBKDF2PasswordHasher

# Classe para personalizar o hash PBKDF2, ajustando o custo de hash em iterations.
class CustomPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    iterations = 600_000
