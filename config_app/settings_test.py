from .settings import *

# Banco em memória só para os testes: não precisa de permissão no MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}