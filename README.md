# Teacher Hub
🟡 Em desenvolvimento

Plataforma de gestão voltada às necessidades dos professores, desenvolvida como parte do Projeto Integrador da disciplina de Políticas de Segurança da Informação.

**Autores**

- Igor Thebas Souza Santos
- Maria Fernanda da Silva Pires
- Uriel Erick Menezes de Oliveira

---

O projeto tem como objetivo desenvolver uma solução que centralize e facilite atividades relacionadas à rotina docente, reduzindo o tempo gasto em tarefas administrativas e permitindo que o professor tenha maior controle sobre suas turmas, avaliações, conteúdos e desempenho dos alunos.

Diferentemente de soluções educacionais tradicionalmente focadas no aluno, o projeto tem como público principal o **professor**, buscando compreender e atender às principais dificuldades encontradas em sua rotina.

## Objetivo

O Teacher Hub busca centralizar diferentes atividades da rotina do professor em uma única plataforma, oferecendo ferramentas para:

- Gerenciamento de turmas e alunos;
- Planejamento e organização de aulas;
- Criação e gerenciamento de avaliações;
- Banco de questões e geração de provas com diferentes versões;
- Correção automática de avaliações;
- Gerenciamento de notas e acompanhamento do desempenho das turmas;
- Organização de materiais e conteúdos;
- Geração de relatórios e indicadores.

## Público-alvo

O sistema tem como público-alvo principal **professores e docentes de instituições de ensino**, buscando auxiliar na organização e execução de atividades relacionadas à sua rotina acadêmica.

## Foco desta etapa

O foco atual é a **camada de segurança da informação**: autenticação, gestão de credenciais, recuperação de senha, criptografia, conformidade com a LGPD e auditoria. As funcionalidades pedagógicas ainda não foram implementadas (o app `gestao_app` é apenas um esqueleto).

## O que já existe

| Área | Situação |
|---|---|
| Cadastro com validação de senha | ✅ Implementado |
| Hash de senha PBKDF2 com salt | ✅ Implementado |
| 2FA (TOTP) após a senha | ✅ Implementado |
| Segredo TOTP cifrado em repouso (Fernet) | ✅ Implementado |
| Bloqueio por tentativas (Django Axes) | ✅ Implementado |
| Sessão com expiração e logout | ✅ Implementado |
| Recuperação de senha com token | ✅ Implementado |
| HTTPS, HSTS e cookies seguros (produção) | ✅ Implementado |
| LGPD: consentimento, consulta, exportação e exclusão | ✅ Implementado |
| Logs com cadeia de integridade (HMAC-SHA256) | ✅ Implementado |
| Pipeline DevSecOps (SAST, DAST, SBOM, segredos) | ✅ Implementado |
| Testes automatizados | 🟡 Pendente |
| Funcionalidades pedagógicas (turmas, provas, notas) | 🔴 Planejado |

## Tecnologias

- **Front-end:** HTML5, CSS3, JavaScript
- **Back-end:** Python 3.12, Django 6.1
- **Banco de dados:** MySQL 8.4
- **Segurança:** PyOTP, `cryptography` (Fernet), django-axes, WhiteNoise
- **Infraestrutura:** Docker e Docker Compose
- **Controle de versão:** Git e GitHub

## Estrutura

- `authenticate_user/`: cadastro, login, 2FA, logout, recuperação de senha, cifra e logs de integridade
- `compliance/`: direitos do titular (consulta, exportação, exclusão e consentimento)
- `config_app/`: configurações do projeto e do hash de senhas
- `gestao_app/`: gestão acadêmica (planejado)
- `.github/workflows/`: pipeline DevSecOps

## Como executar

Com Docker:

```bash
docker compose up --build
```

A aplicação fica em `http://localhost:8000`. As variáveis do `docker-compose.yaml` são apenas para teste e não devem ser usadas em produção.

Sem Docker, crie a pasta `logs/` e um arquivo `.env` com as variáveis abaixo, depois rode `pip install -r requirements.txt`, `python manage.py migrate` e `python manage.py runserver`:

```env
DJANGO_SECRET=
APP_STATE=False            # True = produção (HTTPS, HSTS, cookies Secure, DEBUG=False)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
EMAIL_HOST=
EMAIL_HOST_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
LOG_INTEGRITY_KEY=         # segredo do HMAC dos logs
CHAVE_CRIPTOGRAFIA=        # chave Fernet
```

Nenhum segredo é versionado. Para verificar a integridade dos logs: `python manage.py verify_logs`.

## Funcionalidades pedagógicas planejadas

- Gerenciamento de turmas, alunos e disciplinas
- Criação de avaliações, banco de questões e provas com versões embaralhadas
- Correção automática, cálculo de notas e indicadores de desempenho
- Planejamento de aulas e organização de materiais

## Release

As versões estáveis são disponibilizadas por meio de Releases no GitHub.