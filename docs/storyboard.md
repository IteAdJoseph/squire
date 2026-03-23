# Storyboard do Produto

## Objetivo
Este documento descreve o fluxo narrativo principal do produto para alinhar decisões de implementação, UX e regras de negócio.

## Escopo
Produto SaaS enxuto para:
- confirmação de horários
- cobrança de sinal e saldo via Pix
- lembretes por WhatsApp
- controle de acesso do tenant com billing simples

## Atores
- **A1 — Dono do SaaS**: operador da plataforma e administrador global
- **A2 — Admin do Tenant**: cliente pagante que usa o sistema no dia a dia
- **A3 — Cliente Final**: pessoa que agenda e paga sinal/saldo
- **A4 — Sistema**: API, worker, scheduler e regras automáticas

## Princípios do Produto
1. O sistema deve ser simples para pequenos negócios.
2. Billing interno é a fonte de verdade para acesso.
3. No início, a cobrança do tenant é manual via Pix.
4. O sistema deve funcionar mesmo sem integrações avançadas.
5. Mudanças críticas devem ser auditáveis.

---

## SB-01 — Onboarding do Tenant

### Contexto
O dono do SaaS fecha um novo cliente pagante.

### Trigger
A1 decide criar uma nova conta para um pequeno negócio.

### Objetivo do ator
Permitir que o novo tenant entre no sistema e comece a operar.

### Fluxo narrativo
1. A1 cria um novo tenant.
2. A1 cria o usuário inicial do tenant.
3. A1 define o plano, o valor mensal e o dia de vencimento.
4. A1 define o billing inicial como `trial` ou `active`.
5. O sistema grava `billing_account` e libera acesso do tenant.
6. O tenant recebe suas credenciais ou redefine a senha.

### Resultado esperado
O tenant existe, tem um usuário inicial e consegue acessar o sistema.

### Regras importantes
- O tenant só pode entrar se `access_status = enabled`.
- A cobrança do tenant não depende inicialmente de integração externa.
- O banco interno é a fonte de verdade do acesso.

---

## SB-02 — Primeiro Acesso do Tenant

### Contexto
O admin do tenant tenta entrar no sistema.

### Trigger
A2 acessa a tela de login.

### Objetivo do ator
Entrar no painel e usar o sistema normalmente.

### Fluxo narrativo
1. A2 informa e-mail/username e senha.
2. O sistema autentica o usuário.
3. O sistema verifica o tenant associado.
4. O sistema consulta `billing_accounts`.
5. O sistema avalia `billing_status` e `access_status`.
6. Se o tenant estiver apto, o login é concluído.
7. Se o tenant estiver suspenso ou cancelado, o login é bloqueado.

### Resultado esperado
Acesso liberado apenas para tenants adimplentes ou em tolerância.

### Regras importantes
- `trial`, `active` e `grace` permitem acesso.
- `late`, `suspended` e `cancelled` bloqueiam acesso.
- A regra de acesso deve existir no login e em rotas autenticadas.

---

## SB-03 — Cadastro Operacional Inicial

### Contexto
O tenant entrou no sistema e precisa preparar o ambiente.

### Trigger
A2 acessa o painel pela primeira vez.

### Objetivo do ator
Cadastrar os dados mínimos para começar a operar.

### Fluxo narrativo
1. A2 cadastra clientes.
2. A2 cadastra serviços.
3. A2 define preço total, duração e valor do sinal.
4. O sistema valida os dados.
5. O sistema deixa o tenant pronto para criar agendamentos.

### Resultado esperado
O tenant consegue operar sem depender de configurações complexas.

### Regras importantes
- Cliente deve ter telefone válido para WhatsApp.
- Serviço deve ter preço total e, opcionalmente, valor de sinal.
- O cadastro deve ser o mais simples possível.

---

## SB-04 — Criação de Agendamento com Sinal

### Contexto
O tenant vai atender um cliente final.

### Trigger
A2 cria um novo agendamento.

### Objetivo do ator
Registrar o compromisso e cobrar o sinal.

### Fluxo narrativo
1. A2 escolhe o cliente.
2. A2 escolhe o serviço.
3. A2 define data e hora.
4. O sistema calcula preço total, sinal e saldo.
5. O agendamento nasce em `awaiting_deposit` quando houver sinal.
6. O sistema gera uma cobrança Pix.
7. O sistema registra a cobrança no histórico.

### Resultado esperado
O agendamento fica pendente de confirmação por pagamento do sinal.

### Regras importantes
- Um agendamento pode ter sinal e saldo.
- Se não houver sinal, o fluxo pode confirmar manualmente.
- A geração da cobrança deve ser auditável.

---

## SB-05 — Confirmação do Sinal

### Contexto
O cliente final pagou o sinal.

### Trigger
O pagamento é confirmado manualmente ou por integração futura.

### Objetivo do ator
Garantir que o horário está confirmado.

### Fluxo narrativo
1. A2 verifica o pagamento ou o sistema recebe um webhook futuro.
2. O sistema marca a cobrança como `paid`.
3. O sistema cria um registro em `billing_payments` do tenant final, se aplicável ao fluxo.
4. O sistema muda o agendamento para `confirmed`.
5. O sistema agenda o lembrete de atendimento.

### Resultado esperado
O horário fica confirmado e pronto para lembrete posterior.

### Regras importantes
- Toda confirmação deve ficar auditada.
- O histórico de cobrança não pode ser perdido.
- No MVP, a confirmação pode ser manual pelo admin.

---

## SB-06 — Lembrete Antes do Atendimento

### Contexto
O horário está próximo.

### Trigger
Chega o momento de enviar lembrete automático.

### Objetivo do ator
Reduzir no-show e reforçar o compromisso.

### Fluxo narrativo
1. O scheduler identifica agendamentos confirmados próximos do horário.
2. O worker prepara a mensagem.
3. O sistema envia o lembrete via WhatsApp.
4. O sistema grava o status do envio.

### Resultado esperado
O cliente final recebe o lembrete antes do atendimento.

### Regras importantes
- O lembrete deve ser enviado uma única vez por janela configurada.
- O envio deve respeitar consentimento e regras do canal.
- Falhas devem ser registradas e retentadas com limite.

---

## SB-07 — Conclusão do Atendimento e Cobrança de Saldo

### Contexto
O atendimento aconteceu.

### Trigger
A2 marca o agendamento como concluído.

### Objetivo do ator
Registrar o atendimento e cobrar o saldo remanescente.

### Fluxo narrativo
1. A2 abre o detalhe do agendamento.
2. A2 marca o atendimento como `completed`.
3. O sistema verifica se existe saldo pendente.
4. Se houver saldo, A2 pode gerar nova cobrança.
5. O sistema registra a cobrança de saldo.
6. O sistema pode enviar a cobrança ao cliente final.

### Resultado esperado
O atendimento é concluído e o saldo pode ser cobrado de forma simples.

### Regras importantes
- Sinal e saldo são cobranças distintas.
- O histórico completo deve permanecer acessível.
- O agendamento concluído não deve perder vínculo com as cobranças.

---

## SB-08 — Inadimplência do Tenant e Suspensão de Acesso

### Contexto
O cliente do SaaS deixou de pagar a mensalidade.

### Trigger
Chega o vencimento do tenant e não há pagamento confirmado.

### Objetivo do ator
Controlar acesso sem planilha como fonte primária.

### Fluxo narrativo
1. O job diário verifica `billing_accounts`.
2. Se o período venceu, o sistema calcula tolerância.
3. Durante a tolerância, o tenant pode ficar em `grace`.
4. Após a tolerância, o sistema muda o tenant para `suspended`.
5. O acesso do tenant é bloqueado.
6. Quando A1 marcar novo pagamento, o acesso pode ser reativado.

### Resultado esperado
O sistema controla o acesso do tenant com base no banco interno.

### Regras importantes
- A fonte de verdade é `billing_accounts`.
- Planilhas externas nunca decidem o acesso em tempo real.
- Reativação deve ser simples e auditável.

---

## SB-09 — Reativação do Tenant

### Contexto
O tenant pagou após suspensão.

### Trigger
A1 recebe Pix e confirma o pagamento.

### Objetivo do ator
Liberar o acesso novamente sem reconfigurar a conta.

### Fluxo narrativo
1. A1 localiza o tenant no admin.
2. A1 registra pagamento manual.
3. O sistema cria um item em `billing_payments`.
4. O sistema atualiza `current_period_start`, `current_period_end` e `next_due_date`.
5. O sistema muda `billing_status` para `active`.
6. O sistema muda `access_status` para `enabled`.

### Resultado esperado
O tenant volta a operar normalmente.

### Regras importantes
- Reativação não recria tenant.
- Dados operacionais do tenant devem ser preservados.
- Toda mudança de status deve gerar auditoria.

---

## Resumo dos estados principais

### Billing do tenant
- `trial`
- `active`
- `grace`
- `late`
- `suspended`
- `cancelled`

### Acesso do tenant
- `enabled`
- `disabled`

### Agendamento
- `draft`
- `awaiting_deposit`
- `confirmed`
- `completed`
- `cancelled`
- `no_show`

### Cobrança
- `pending`
- `paid`
- `expired`
- `cancelled`
- `overdue`

---

## Decisões fixas para agentes
1. Billing interno é a fonte de verdade.
2. Cobrança inicial do tenant é manual via Pix.
3. Planilha externa não decide autorização.
4. Fluxos devem ser auditáveis.
5. Simplicidade operacional vale mais que automação total no MVP.