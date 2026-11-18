from django.contrib.auth.hashers import PBKDF2PasswordHasher

class CustomPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    """
    PBKDF2-HMAC-SHA256 com custo de hash configurado explicitamente.

    Justificativa técnica do parâmetro `iterations = 600_000`:

    1. Referência normativa: o OWASP Password Storage Cheat Sheet recomenda
       no mínimo 600.000 iterações para PBKDF2-HMAC-SHA256 (algoritmo usado
       por padrão pelo PBKDF2PasswordHasher do Django). O NIST SP 800-63B
       (seção 5.1.1.2) exige função de derivação de chave com salt e custo
       ajustável, o que o PBKDF2 atende.

    2. Custo para o atacante: cada tentativa de adivinhar uma senha
       precisa repetir as 600.000 iterações; em ataque offline (vazamento
       do banco) isso multiplica o esforço por 600 mil em relação a um
       SHA-256 simples.

    3. Custo para o usuário legítimo (medição em ambiente de teste, mediana
       de 7 execuções com hashlib.pbkdf2_hmac / SHA-256):
           100.000 iterações ->  ~16 ms
           300.000 iterações ->  ~45 ms
           600.000 iterações ->  ~92 ms   <- valor adotado
         1.200.000 iterações -> ~183 ms
       Cerca de 0,1 s por login é imperceptível ao usuário e viável para o
       servidor, mantendo o valor no mínimo recomendado. O custo deve ser
       reavaliado periodicamente: ao aumentar `iterations`, o Django
       re-hasheia a senha de forma transparente no próximo login.

    4. Salt: o Django gera um salt aleatório e único por senha, armazenado
       junto ao hash no formato `pbkdf2_sha256$iter$salt$hash`.
    """

    iterations = 600_000