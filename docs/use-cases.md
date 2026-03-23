# Casos de Uso do Produto

## Objetivo
Este documento descreve os casos de uso do MVP em formato operacional e consultável por agentes.

## Convenções
- **UC-XX**: identificador estável do caso de uso
- **Atores**: quem participa
- **Pré-condições**: o que precisa ser verdade antes
- **Fluxo principal**: caminho esperado
- **Fluxos alternativos**: exceções ou desvios
- **Pós-condições**: estado esperado ao final
- **Regras de negócio**: invariantes importantes

---

# UC-01 — Criar tenant

## Atores
- Primário: Dono do SaaS
- Secundário: Sistema

## Pré-condições
- O dono do SaaS está autenticado no admin global.
- Ainda não existe tenant com o mesmo `slug`.

## Fluxo principal
1. O dono informa nome e slug do tenant.
2. O sistema valida unicidade do slug.
3. O sistema cria o tenant.
4. O sistema registra auditoria.

## Fluxos alternativos
### A1 — Slug já existe
1. O sistema rejeita a criação.
2. O sistema informa erro de unicidade.

## Pós-condições
- O tenant existe e pode receber usuários e billing.

## Regras de negócio
- `slug` deve ser único.
- Tenant não nasce sem identificação mínima.

---

# UC-02 — Criar usuário inicial do tenant

## Atores
- Primário: Dono do SaaS
- Secundário: Sistema

## Pré-condições
- O tenant já existe.
- O e-mail e username ainda não existem dentro do mesmo tenant.

## Fluxo principal
1. O dono informa e-mail, username e papel inicial.
2. O sistema cria o usuário vinculado ao tenant.
3. O sistema marca `is_active = true`.
4. O sistema registra auditoria.

## Fluxos alternativos
### A1 — E-mail já existe no tenant
1. O sistema bloqueia a operação.
2. O sistema retorna erro de unicidade.

## Pós-condições
- O tenant tem ao menos um usuário ativo.

## Regras de negócio
- Unicidade é por tenant.
- O usuário inicial pode ser `owner`.

---

# UC-03 — Configurar billing do tenant

## Atores
- Primário: Dono do SaaS
- Secundário: Sistema

## Pré-condições
- O tenant já existe.

## Fluxo principal
1. O dono define plano, preço mensal, dia de vencimento e provider.
2. O dono define status inicial como `trial` ou `active`.
3. O sistema calcula período corrente.
4. O sistema cria `billing_account`.
5. O sistema registra auditoria.

## Fluxos alternativos
### A1 — Dia de vencimento inválido
1. O sistema rejeita o valor.
2. O sistema pede ajuste.

## Pós-condições
- O tenant passa a ter uma conta de billing ativa no banco.

## Regras de negócio
- Billing do tenant é obrigatório para controle de acesso.
- Provider inicial padrão é `manual_pix`.

---

# UC-04 — Login do usuário do tenant

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- Usuário existe.
- Senha está correta.
- Tenant associado existe.

## Fluxo principal
1. O usuário informa credenciais.
2. O sistema autentica.
3. O sistema carrega o tenant.
4. O sistema consulta `billing_account`.
5. O sistema calcula o estado de acesso.
6. O sistema libera a sessão se houver permissão.

## Fluxos alternativos
### A1 — Credenciais inválidas
1. O sistema rejeita o login.

### A2 — Tenant suspenso ou cancelado
1. O sistema rejeita o login.
2. O sistema informa status incompatível com acesso.

## Pós-condições
- Sessão autenticada ou acesso negado.

## Regras de negócio
- `trial`, `active` e `grace` permitem acesso.
- `late`, `suspended` e `cancelled` bloqueiam acesso.
- `access_status = disabled` sempre bloqueia.

---

# UC-05 — Cadastrar cliente final

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- Tenant autenticado e com acesso liberado.

## Fluxo principal
1. O admin informa nome e telefone.
2. O sistema valida dados mínimos.
3. O sistema cria o cliente final.
4. O sistema registra auditoria.

## Fluxos alternativos
### A1 — Telefone inválido
1. O sistema rejeita cadastro.

## Pós-condições
- O cliente final fica disponível para agendamentos.

## Regras de negócio
- Telefone deve ser válido para contato operacional.
- O cadastro deve ser simples.

---

# UC-06 — Cadastrar serviço

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- Tenant autenticado e com acesso liberado.

## Fluxo principal
1. O admin informa nome, duração, preço total e sinal opcional.
2. O sistema valida os campos.
3. O sistema cria o serviço.

## Fluxos alternativos
### A1 — Sinal maior que o preço total
1. O sistema rejeita a criação.

## Pós-condições
- O serviço pode ser usado em agendamentos.

## Regras de negócio
- `deposit_amount <= total_price`
- Serviço deve ter estrutura mínima operacional.

---

# UC-07 — Criar agendamento

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- Cliente final existe.
- Serviço existe.
- Tenant está com acesso liberado.

## Fluxo principal
1. O admin seleciona cliente.
2. O admin seleciona serviço.
3. O admin define data e hora.
4. O sistema calcula preço, sinal e saldo.
5. O sistema cria o agendamento.
6. Se houver sinal, o status inicial é `awaiting_deposit`.
7. Se não houver sinal, o status pode iniciar como `confirmed` ou `draft` conforme regra futura.

## Fluxos alternativos
### A1 — Conflito de horário
1. O sistema rejeita ou alerta o conflito.

## Pós-condições
- O agendamento existe e pode gerar cobrança.

## Regras de negócio
- O cálculo financeiro deve ficar persistido no agendamento.
- O vínculo com cliente e serviço é obrigatório.

---

# UC-08 — Gerar cobrança de sinal

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- O agendamento existe.
- O serviço prevê sinal.

## Fluxo principal
1. O admin solicita a geração da cobrança.
2. O sistema cria uma cobrança `pending`.
3. O sistema associa a cobrança ao agendamento.
4. O sistema registra referência externa se houver integração futura.
5. O sistema torna a cobrança visível no detalhe do agendamento.

## Fluxos alternativos
### A1 — Agendamento sem sinal
1. O sistema não gera cobrança de sinal.
2. O sistema informa que não há valor de sinal configurado.

## Pós-condições
- Existe uma cobrança de sinal pendente.

## Regras de negócio
- Sinal e saldo são entidades separadas.
- A cobrança deve ser auditável.

---

# UC-09 — Confirmar pagamento do sinal manualmente

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- A cobrança existe e está `pending`.

## Fluxo principal
1. O admin abre a cobrança.
2. O admin marca a cobrança como paga.
3. O sistema cria um registro de pagamento.
4. O sistema atualiza a cobrança para `paid`.
5. O sistema altera o agendamento para `confirmed`.
6. O sistema agenda lembrete futuro.

## Fluxos alternativos
### A1 — Cobrança já paga
1. O sistema impede duplicidade.

## Pós-condições
- O horário fica confirmado.

## Regras de negócio
- Operação deve ser idempotente.
- Mudança de estado deve ficar em auditoria.

---

# UC-10 — Enviar lembrete de atendimento

## Atores
- Primário: Sistema
- Secundário: Cliente final

## Pré-condições
- O agendamento está `confirmed`.
- Existe telefone válido.
- Existe consentimento/canal habilitado quando necessário.

## Fluxo principal
1. O scheduler detecta lembrete devido.
2. O worker prepara mensagem.
3. O sistema envia mensagem.
4. O sistema grava status do envio.

## Fluxos alternativos
### A1 — Envio falha
1. O sistema registra falha.
2. O sistema agenda retry conforme política.

## Pós-condições
- O lembrete fica registrado como enviado, entregue, lido ou falho.

## Regras de negócio
- O mesmo lembrete não deve ser duplicado indevidamente.
- Retries devem ter limite.

---

# UC-11 — Concluir atendimento

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- O agendamento está `confirmed`.

## Fluxo principal
1. O admin abre o detalhe do agendamento.
2. O admin marca o atendimento como `completed`.
3. O sistema registra auditoria.
4. O sistema calcula se existe saldo remanescente.

## Fluxos alternativos
### A1 — Agendamento cancelado
1. O sistema não permite concluir.

## Pós-condições
- O atendimento fica concluído.

## Regras de negócio
- Apenas `confirmed` pode virar `completed`.
- A transição precisa seguir state machine.

---

# UC-12 — Gerar cobrança de saldo

## Atores
- Primário: Admin do tenant
- Secundário: Sistema

## Pré-condições
- O agendamento está `completed`.
- Existe saldo pendente maior que zero.

## Fluxo principal
1. O admin solicita cobrança do saldo.
2. O sistema cria nova cobrança `pending`.
3. O sistema vincula a cobrança ao agendamento.
4. O sistema registra histórico.

## Fluxos alternativos
### A1 — Saldo zero
1. O sistema não gera cobrança.

## Pós-condições
- O saldo passa a ter cobrança própria.

## Regras de negócio
- Cobrança de saldo não substitui a de sinal.
- Ambas devem coexistir no histórico.

---

# UC-13 — Suspender tenant por inadimplência

## Atores
- Primário: Sistema
- Secundário: Dono do SaaS

## Pré-condições
- Existe `billing_account` do tenant.
- O período venceu sem pagamento.

## Fluxo principal
1. O job diário carrega tenants vencidos.
2. O sistema verifica tolerância.
3. Se ainda estiver no limite, marca `grace`.
4. Se ultrapassou o limite, marca `suspended`.
5. O sistema muda `access_status` para `disabled`.
6. O sistema registra auditoria.

## Fluxos alternativos
### A1 — Tenant cancelado
1. O sistema não executa suspensão redundante.

## Pós-condições
- O tenant fica impedido de acessar o sistema.

## Regras de negócio
- Fonte de verdade é `billing_accounts`.
- A decisão não depende de planilha em tempo real.

---

# UC-14 — Reativar tenant após pagamento manual

## Atores
- Primário: Dono do SaaS
- Secundário: Sistema

## Pré-condições
- O tenant está `late`, `grace` ou `suspended`.

## Fluxo principal
1. O dono registra pagamento manual.
2. O sistema cria `billing_payment`.
3. O sistema recalcula o período corrente.
4. O sistema marca `billing_status = active`.
5. O sistema marca `access_status = enabled`.
6. O sistema registra auditoria.

## Fluxos alternativos
### A1 — Pagamento inválido
1. O sistema não altera status.

## Pós-condições
- O tenant volta a acessar o sistema.

## Regras de negócio
- Reativação não apaga histórico anterior.
- O tenant preserva seus dados operacionais.

---

# UC-15 — Cancelar tenant

## Atores
- Primário: Dono do SaaS
- Secundário: Sistema

## Pré-condições
- O tenant existe.

## Fluxo principal
1. O dono escolhe cancelar.
2. O sistema marca `billing_status = cancelled`.
3. O sistema marca `access_status = disabled`.
4. O sistema registra `cancelled_at`.
5. O sistema registra auditoria.

## Fluxos alternativos
### A1 — Tenant já cancelado
1. O sistema mantém o estado.

## Pós-condições
- O tenant não acessa mais o sistema.

## Regras de negócio
- Cancelamento não deve destruir dados automaticamente.
- Exclusão física é decisão separada do cancelamento.

---

# Regras de negócio globais

## RB-01 — Fonte de verdade
O banco interno da aplicação é a fonte de verdade para billing e autorização.

## RB-02 — Planilhas
Planilhas externas podem servir como apoio operacional, mas nunca como fonte de verdade em tempo real.

## RB-03 — Acesso
Acesso depende de `billing_status` e `access_status`.

## RB-04 — Auditoria
Toda mudança crítica de billing, acesso, autenticação, cobrança e estado de agendamento deve gerar auditoria.

## RB-05 — Simplicidade
No MVP, priorizar simplicidade operacional sobre automação completa.

## RB-06 — Integrações futuras
O desenho deve permitir futuro acoplamento com Asaas, Mercado Pago ou outro PSP, sem reescrever a lógica central de billing interno.

## RB-07 — Idempotência
Confirmações de pagamento e webhooks futuros devem ser idempotentes.

## RB-08 — Multi-tenant
Todo dado operacional pertence a um tenant e deve respeitar isolamento por `tenant_id`.

---

# Checklist para agentes antes de implementar mudanças

1. O caso de uso afetado está identificado por ID?
2. A mudança altera fluxo principal ou fluxo alternativo?
3. Há impacto em billing, auth, webhook ou state machine?
4. Há nova regra de negócio implícita?
5. A auditoria foi preservada?
6. O comportamento está alinhado com `AGENTS.md`?