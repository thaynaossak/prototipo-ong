# ONG Lotus — Gestão de atendimentos

Aplicação web responsiva para a ONG Lotus, Jardim Cumbica, Guarulhos. Organiza famílias, integrantes, lista de espera e histórico de cestas básicas e leite. Projeto acadêmico alinhado ao ODS 2, meta 2.1. Não integra sistemas governamentais, não decide elegibilidade e não amplia por si só as doações.

## O que já funciona

- Login/logout, recuperação de senha por email, hash PBKDF2, limite de tentativas e sessão de 30 minutos de inatividade.
- Perfis Colaborador e Gestor, verificados no servidor.
- Cadastro e edição de famílias com vários integrantes e exatamente um responsável.
- Alertas de possíveis duplicidades por nome normalizado e nascimento, com confirmação humana.
- Situação familiar e lista de espera ordenada por solicitação, controladas pelo gestor.
- Registro de entrega, agendamento e confirmação de ausência. Ausência não inativa a família.
- Histórico, paginação de 20 itens e filtro opcional por datas (RF09).
- Persistência, transações e chave idempotente assinada para evitar reenvio da mesma operação.
- Formulários rotulados, foco visível, controles de 48px, texto + símbolo para estados, layout responsivo.

## Tecnologia e arquitetura

Python 3.12, Django 5.2 LTS, PostgreSQL (produção), SQLite (desenvolvimento), Gunicorn e WhiteNoise. Monólito MVT com serviços: `templates/` apresenta, `core/views.py` autoriza/orquestra, `core/forms.py` valida, `core/services.py` aplica operações atômicas e `core/models.py` persiste pelo ORM. Usuário nativo Django + Família 1:N Integrante e Família 1:N Atendimento; cada atendimento pertence a um usuário.

## Executar no computador

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Defina variáveis na sua sessão (PowerShell: `$env:NOME='valor'`). A aplicação não carrega `.env` automaticamente fora do Docker.

```bash
export DEBUG=1
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(64))')"
python manage.py migrate
python manage.py setup_roles
python manage.py seed_demo
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Abra http://127.0.0.1:8000. O superusuário é o administrador técnico, não uma conta compartilhada. Os registros de `seed_demo` são exclusivamente fictícios; nenhuma senha é criada por esse comando. Para contas de operação, confirme o email com o responsável e use convite:

```bash
# Configure SMTP antes. Use um domínio HTTPS seu, sem caminho.
python manage.py invite_user nome_usuario email_confirmado --role Colaborador --domain seu-dominio.example
```

O comando envia um link de definição de senha válido por 30 minutos, sem divulgar senha inicial. Gestores operacionais não administram usuários pelo menu comum: convites são executados pelo administrador técnico; o painel /admin/ fica restrito a staff. Para conceder staff, use administração técnica deliberada. Em desenvolvimento pode-se usar `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`; o link impresso no terminal é segredo temporário e não deve ser compartilhado.

## PostgreSQL com Docker

```bash
cp .env.example .env
# Edite SECRET_KEY e POSTGRES_PASSWORD com valores aleatórios próprios.
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py setup_roles
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
```

O Compose mantém o banco em volume e expõe o web apenas em 127.0.0.1:8000. Não exponha DEBUG=1 na internet. Para PostgreSQL gerenciado fora do Compose, configure `DATABASE_URL`, preferencialmente com `sslmode=require`. SQLite é só a alternativa local; teste de concorrência deve usar PostgreSQL.

## Implantação real

Este repositório é Django/WSGI: uma hospedagem exclusivamente estática, inclusive o Site do protótipo anterior, NÃO executa este back-end. Escolha hospedagem Linux/Python ou contêiner com PostgreSQL; veja `docs/implantacao.md`. Não foram contratados servidores externos ou planos pagos nesta entrega. O protótipo HTML anterior foi preservado em `prototipo/index.html`, independente da aplicação real.

## Verificar

```bash
pip install -r requirements-dev.txt
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py check
pip-audit -r requirements.txt
# Com variáveis de produção e segredo forte:
python manage.py check --deploy
```

GitHub Actions repete testes com PostgreSQL 16. Resultados locais e limites em `docs/verificacao.md`. Não confundir testes técnicos com validação real de Seu Tião, ainda pendente. O nome completo fictício anteriormente sugerido não é uma identificação confirmada do parceiro.

## Limites

Sem finanças, estoque, captação, notificações automáticas, integrações governamentais, aplicativo nativo ou funcionamento offline. Não há exclusão de famílias no fluxo; status inativa preserva histórico. Direito de remoção/retificação e prazo de retenção devem ser acordados com a ONG antes de dados reais. Todos os operadores autorizados compartilham a base da única ONG; não é sistema multi-instituição.
