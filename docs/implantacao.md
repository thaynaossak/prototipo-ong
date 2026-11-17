# Implantação e operação

1. Provisionar Python 3.12/Linux (ou Dockerfile), domínio com certificado TLS e PostgreSQL. Confirmar preço, RAM, armazenamento, limite de conexões, suspensão por inatividade, backups e região antes de escolher plano; não assumir gratuidade.
2. Instalar requirements, configurar SECRET_KEY aleatória de pelo menos 50 caracteres, DEBUG=0, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS com origens HTTPS e DATABASE_URL do banco. Configurar SMTP e remetente verificado. Não versionar valores reais.
3. Executar migrate, setup_roles, collectstatic e createsuperuser uma vez. Iniciar `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2` com supervisor e proxy HTTPS. Usar TRUST_PROXY=1 somente se o proxy confiável remover cabeçalhos encaminhados pelo cliente e fornecer X-Forwarded-Proto correto. A porta interna não deve ser acessível fora do proxy.
4. Executar check --deploy, testar login, permissões e SMTP. Verificar política de conteúdo, CSRF e cookies no domínio final. Não carregar dados reais antes da revisão de acesso e consentimento.
5. Atualizar dependências após auditoria e regressão; garantir rollback do código com compatibilidade de migrations. Não executar migrations automaticamente em cada worker.

## Backups

Configurar backup automático diário no serviço gerenciado, retenção mínima de sete dias, acesso separado restrito e criptografia. Se não houver recurso, o operador deve agendar `pg_dump --format=custom` com credenciais por secret store/.pgpass protegido, salvar em armazenamento privado criptografado e aplicar retenção. O aplicativo não instala um agendador de infraestrutura. Mensalmente restaurar com pg_restore em um banco de teste vazio, conferir quantidade de famílias/atendimentos e registrar evidência. Nunca restaurar testes sobre produção. Documentar responsáveis, custo e procedimento de recuperação antes de uso real.

## Tentativas e logs

Axes armazena falhas no banco: cinco tentativas por conta OU IP limitam por 15 minutos. Atenção ao IP compartilhado da ONG; revisar após piloto e não confiar em X-Forwarded-For fornecido livremente. Agendar `python manage.py axes_reset_logs 30` conforme política de retenção. Não registrar senhas, tokens de convite ou corpos de formulários em proxies/logs. Desativar conta em vez de excluí-la.

## Desempenho

Preparar 1.000 famílias, 3.000 integrantes e 10.000 atendimentos fictícios num banco de teste. Usar o mesmo celular Android (>=2GB RAM, quatro núcleos), navegador, versão, cache e pesquisa, com paginação de 20 itens. Rede de referência 1,5Mbps/750Kbps e 150ms. Uma execução de aquecimento + cinco medições, do envio até resultado utilizável, com Network/Performance. Meta: mediana <=3s. Registrar rede real e cold start separadamente. Meta não foi aferida no aparelho da ONG. Se falhar, revisar planos de consulta, índices, ativos, compactação e capacidade do host.
