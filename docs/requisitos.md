# Rastreabilidade

| Requisito | Implementação |
|---|---|
| RF01 Cadastro | FamilyForm + inline formset Members, gravação atômica |
| RF02 Consulta | families, busca por integrante, paginação |
| RF03 Edição | family_edit; mantém IDs e histórico |
| RF04 Duplicidade | nome normalizado/nascimento, alerta e revisão humana |
| RF05 Entrega | delivery + record_attendance, quantidades validadas, chave assinada e única |
| RF06 Ausência | agendamento explícito no mesmo formulário, mark_absent apenas para previstos não futuros |
| RF07 Histórico | family_detail com usuário, data, estado e itens |
| RF08 Espera | change_status requer manage_waitlist; ordenação por solicitação |
| RF09 Desejável | filtro de datas implementado após núcleo |
| RNF01 | auth nativa, PBKDF2, Axes, idle middleware, HTTPS em produção |
| RNF02 | ORM, Forms, escape, CSRF, CSP, variáveis de ambiente, auditoria |
| RNF03 | README/Docker, Postgres, WhiteNoise, teste móvel planejado |
| RNF04 | HTML semântico, rótulos, foco, alvos 48px, mensagens textuais, responsividade |

Segurança não absoluta; revisão no domínio final é obrigatória. Concessão de alimentos e critérios de prioridade são decisões humanas. O sistema não comprova elegibilidade, nem usa ausências para excluir automaticamente. Endereço e nascimento têm finalidade operacional; saúde, CPF, imagens de documentos e dados bancários não são coletados.

## Limites de entrada das entregas

Quantidade de cestas: inteiro entre 0 e 9.999. Leite: número decimal entre 0 e 999.999, com uma casa decimal. Entregas exigem pelo menos uma quantidade positiva e data não futura; agendamentos exigem quantidades zeradas. As restrições são verificadas no servidor mesmo sem JavaScript. Valores fora da faixa devem produzir mensagem de correção, preservando os demais campos, sem criar atendimento. Esses limites são proteções técnicas contra entradas incompatíveis com o MVP; a ONG continua responsável pelas decisões de atendimento.
