# Verificação técnica

Executada em Python 3.12.14 e SQLite local em 17/11/2026.

- 22 testes automatizados passaram: cadastro atômico, edição com preservação de responsável e histórico, confirmação de duplicidade, entrega idempotente, token adulterado, quantidades e data inválidas, agendamento/ausência, permissões de gestor, login/logout, bloqueio de tentativas, expiração de sessão, CSRF, HTML rejeitado, SQL tratado como dado, headers, restrições de banco e envio de recuperação de senha.
- makemigrations --check --dry-run: sem alterações.
- check --deploy com segredo aleatório forte e DEBUG=0: sem avisos.
- collectstatic: arquivos coletados e compactados.
- pip-audit -r requirements.txt: nenhuma vulnerabilidade conhecida encontrada no momento.

Não executado localmente: concorrência com PostgreSQL, Docker, SMTP externo, aparelho/rede da ONG, meta móvel de 3s, auditoria completa de acessibilidade e validação com representante real. GitHub Actions está configurado para testar com PostgreSQL; seu resultado deve ser consultado separadamente. Backups, HTTPS e retenção exigem infraestrutura configurada conforme docs/implantacao.md.

Regressão adicional: envio de 2.147.483.648 cestas retorna formulário com erro, sem inserir atendimento. O limite de 9.999 cestas é validado no servidor antes da persistência; não é um critério de concessão de alimentos.
