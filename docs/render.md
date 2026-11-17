# Publicação acadêmica no Render

Blueprint render.yaml: web Python e PostgreSQL gratuitos na mesma região (Virginia). Banco acessível apenas pela rede privada. Senhas geradas pelo Render e não versionadas. A conta inicial lotus_admin recebe senha aleatória no ambiente do serviço; apenas o proprietário deve consultar a senha na área Environment e trocar após acesso. Não publique essa senha no trabalho ou no repositório. A criação é idempotente e não redefine senha em reinícios.

O script de build instala dependências, coleta estáticos e verifica configuração. No plano gratuito, migrations e criação dos perfis ocorrem antes do Gunicorn no script de início porque pre-deploy e shell não estão disponíveis. Operação limitada a uma instância; ao escalar, migrar release tasks para pre-deploy separado. SEED_DEMO=1 inclui apenas três famílias fictícias e pode ser desativado no Blueprint.

Monitoramento: Render consulta /health/ sem login. A rota executa SELECT 1 e responde JSON status ok/200; em falha de banco, unavailable/503, sem expor detalhes. Render verifica readiness no deploy e retira/reinicia instâncias após falhas consecutivas conforme a plataforma. Conferir Events, logs e Metrics; alertas dependem das preferências de notificação da conta, não foram configurados destinatários externos.

Limites verificados na documentação Render: web suspende após 15 minutos sem tráfego; retomada pode levar cerca de um minuto; 750 horas gratuitas por workspace/mês; PostgreSQL gratuito tem 1GB e expira após 30 dias, sem backups. Não usar dados reais neste ambiente de auditoria. Tráfego e builds consomem franquias e podem gerar cobrança adicional se houver meio de pagamento configurado; revisar limites no painel. Não foi contratado plano pago. Uso contínuo pela ONG exige banco permanente, política de backup e retenção e validação comunitária.

SMTP nas portas usuais é bloqueado no web gratuito. Recuperação de senha não está operacional neste plano sem provedor de email compatível (API HTTPS) e integração adicional. O administrador consegue redefinir contas pelo painel autenticado; não expor ou compartilhar credenciais entre operadores.
