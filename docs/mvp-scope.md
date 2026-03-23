# MVP Scope — Reminda

## Objetivo
Documento de referência para agentes e desenvolvedores. Define entidades, campos, state machines, fluxos, regras de negócio e superfície de API do MVP.

Leitura obrigatória: `AGENTS.md`, `docs/storyboard.md`, `docs/use-cases.md`.

---

## Produto em uma frase

SaaS multi-tenant enxuto para pequenos negócios confirmarem agendamentos, cobrarem sinal e saldo via Pix e enviarem lembretes no WhatsApp.

---

## Atores

| ID | Ator               | Descrição                                               |
|----|--------------------|---------------------------------------------------------|
| A1 | Dono do SaaS       | Administrador global da plataforma                      |
| A2 | Admin do Tenant    | Cliente pagante que opera o sistema no dia a dia        |
| A3 | Cliente Final      | Pessoa que agenda e paga sinal/saldo                    |
| A4 | Sistema            | API, worker, scheduler e regras automáticas             |

---

## Entidades e Campos

### Tenant

| Campo         | Tipo         | Regras                         |
|---------------|--------------|--------------------------------|
| id            | UUID PK      |                                |
| name          | str          | obrigatório                    |
| slug          | str unique   | único global, imutável         |
| access_status | enum         | `enabled` \| `disabled`        |
| created_at    | datetime UTC |                                |

### BillingAccount (1 por tenant)

| Campo                | Tipo         | Regras                                     |
|----------------------|--------------|--------------------------------------------|
| id                   | UUID PK      |                                            |
| tenant_id            | UUID FK      | único (1 por tenant)                       |
| plan                 | str          | ex: "starter", "pro"                       |
| monthly_price        | Decimal      | >= 0                                       |
| due_day              | int          | 1–28                                       |
| grace_days           | int          | default 5                                  |
| billing_status       | enum         | ver state machine abaixo                   |
| provider             | enum         | `manual_pix` (default no MVP)              |
| current_period_start | date         |                                            |
| current_period_end   | date         |                                            |
| next_due_date        | date         |                                            |
| cancelled_at         | datetime UTC | nullable                                   |
| created_at           | datetime UTC |                                            |
| updated_at           | datetime UTC |                                            |

### BillingPayment (pagamentos do tenant ao SaaS)

| Campo              | Tipo         | Regras                      |
|--------------------|--------------|-----------------------------|
| id                 | UUID PK      |                             |
| billing_account_id | UUID FK      |                             |
| amount             | Decimal      | > 0                         |
| paid_at            | datetime UTC |                             |
| notes              | str          | nullable                    |
| created_by         | UUID FK      | user id do A1 que registrou |
| created_at         | datetime UTC |                             |

### User

| Campo           | Tipo         | Regras                                    |
|-----------------|--------------|-------------------------------------------|
| id              | UUID PK      |                                           |
| tenant_id       | UUID FK      |                                           |
| email           | str          | único por tenant                          |
| username        | str          | único por tenant                          |
| hashed_password | str          |                                           |
| role            | enum         | `owner` \| `admin` \| `operator`          |
| is_active       | bool         | default true                              |
| created_at      | datetime UTC |                                           |

### Customer (cliente final, pertence ao tenant)

| Campo     | Tipo         | Regras                               |
|-----------|--------------|--------------------------------------|
| id        | UUID PK      |                                      |
| tenant_id | UUID FK      |                                      |
| name      | str          | obrigatório                          |
| phone     | str          | formato E.164, obrigatório           |
| notes     | str          | nullable                             |
| is_active | bool         | default true                         |
| created_at| datetime UTC |                                      |

### Service (pertence ao tenant)

| Campo            | Tipo         | Regras                                |
|------------------|--------------|---------------------------------------|
| id               | UUID PK      |                                       |
| tenant_id        | UUID FK      |                                       |
| name             | str          | obrigatório                           |
| duration_minutes | int          | > 0                                   |
| total_price      | Decimal      | >= 0                                  |
| deposit_amount   | Decimal      | >= 0, <= total_price; 0 = sem sinal   |
| is_active        | bool         | default true                          |
| created_at       | datetime UTC |                                       |

### Appointment

| Campo          | Tipo         | Regras                                         |
|----------------|--------------|------------------------------------------------|
| id             | UUID PK      |                                                |
| tenant_id      | UUID FK      |                                                |
| customer_id    | UUID FK      |                                                |
| service_id     | UUID FK      |                                                |
| scheduled_at   | datetime UTC | obrigatório                                    |
| total_price    | Decimal      | snapshot no momento da criação                 |
| deposit_amount | Decimal      | snapshot; 0 = sem sinal                        |
| balance_amount | Decimal      | calculado: total_price - deposit_amount        |
| status         | enum         | ver state machine abaixo                       |
| notes          | str          | nullable                                       |
| created_at     | datetime UTC |                                                |
| updated_at     | datetime UTC |                                                |

### Charge

| Campo          | Tipo         | Regras                                          |
|----------------|--------------|-------------------------------------------------|
| id             | UUID PK      |                                                 |
| tenant_id      | UUID FK      |                                                 |
| appointment_id | UUID FK      |                                                 |
| type           | enum         | `deposit` \| `balance`                          |
| amount         | Decimal      | > 0                                             |
| status         | enum         | ver state machine abaixo                        |
| external_ref   | str          | nullable; reservado para integração PSP futura  |
| paid_at        | datetime UTC | nullable                                        |
| expires_at     | datetime UTC | nullable; para expiração automática futura      |
| created_at     | datetime UTC |                                                 |
| updated_at     | datetime UTC |                                                 |

### Reminder

| Campo          | Tipo         | Regras                              |
|----------------|--------------|-------------------------------------|
| id             | UUID PK      |                                     |
| tenant_id      | UUID FK      |                                     |
| appointment_id | UUID FK      |                                     |
| scheduled_for  | datetime UTC |                                     |
| sent_at        | datetime UTC | nullable                            |
| status         | enum         | `pending` \| `sent` \| `failed`     |
| attempt_count  | int          | default 0                           |
| last_error     | str          | nullable                            |
| created_at     | datetime UTC |                                     |

### AuditLog

| Campo       | Tipo         | Regras                                         |
|-------------|--------------|------------------------------------------------|
| id          | UUID PK      |                                                |
| tenant_id   | UUID FK      | nullable (ações globais do A1 não têm tenant)  |
| user_id     | UUID FK      | nullable (ações do sistema)                    |
| entity_type | str          | ex: "appointment", "charge", "billing_account" |
| entity_id   | UUID         |                                                |
| action      | str          | ex: "created", "status_changed", "paid"        |
| before      | JSONB        | nullable                                       |
| after       | JSONB        | nullable                                       |
| created_at  | datetime UTC |                                                |

---

## State Machines

### BillingAccount — billing_status

```
trial ──────────────────────────────────────────► active
                                                     │
                                                 (venceu)
                                                     │
                                                     ▼
                                                   grace  (dentro do prazo de tolerância; acesso permitido)
                                                   │   │
                                              (pago)  (prazo esgotado)
                                                 │       │
                                                 ▼       ▼
                                              active  suspended  (acesso bloqueado)
                                                         │
                                                      (pago)
                                                         │
                                                         ▼
                                                      active

Qualquer estado ──► cancelled  (decisão do A1; irreversível no MVP)
late = estado que bloqueia acesso, setável manualmente pelo A1 antes da suspensão automática
```

Acesso permitido: `trial`, `active`, `grace`
Acesso bloqueado: `late`, `suspended`, `cancelled`

### Appointment — status

```
                        ┌─ (sem sinal) ─► confirmed
criação ──► draft ──────┤
                        └─ (com sinal) ─► awaiting_deposit ──► confirmed ──► completed
                                                   │                │
                                               cancelled        no_show
                                                               cancelled
```

Transições válidas:
- `draft` → `awaiting_deposit` (deposit_amount > 0)
- `draft` → `confirmed` (deposit_amount == 0)
- `awaiting_deposit` → `confirmed` (UC-09: pagamento confirmado)
- `awaiting_deposit` → `cancelled`
- `confirmed` → `completed` (UC-11)
- `confirmed` → `no_show`
- `confirmed` → `cancelled`

### Charge — status

```
pending ──► paid
        ──► expired
        ──► cancelled
```

---

## Fluxos de Negócio Principais

### Fluxo 1 — Onboarding do tenant (SB-01)
1. A1 cria tenant (UC-01)
2. A1 cria usuário inicial (UC-02)
3. A1 configura billing (UC-03)
4. Tenant acessa com `trial` ou `active`

### Fluxo 2 — Operação diária (SB-03 a SB-07)
1. A2 cadastra clientes e serviços (UC-05, UC-06)
2. A2 cria agendamento → sistema calcula valores (UC-07)
3. Sistema (ou A2) gera cobrança de sinal (UC-08)
4. A2 confirma pagamento manualmente (UC-09)
5. Scheduler agenda lembrete de atendimento
6. Worker envia lembrete via WhatsApp (UC-10)
7. A2 conclui atendimento (UC-11)
8. A2 gera cobrança de saldo se houver (UC-12)

### Fluxo 3 — Inadimplência e reativação (SB-08, SB-09)
1. Job diário avalia `billing_accounts` com `next_due_date` vencida
2. Dentro do `grace_days`: status → `grace`
3. Além do `grace_days`: status → `suspended`, `access_status` → `disabled`
4. A1 registra pagamento manual (UC-14)
5. Sistema recalcula período, status → `active`, acesso → `enabled`

---

## Regras de Negócio

| ID    | Regra                                                                                                           |
|-------|-----------------------------------------------------------------------------------------------------------------|
| RB-01 | Banco interno é fonte de verdade para billing e autorização                                                     |
| RB-02 | Planilhas externas nunca decidem acesso em tempo real                                                           |
| RB-03 | Acesso depende de `billing_status` E `access_status`                                                            |
| RB-04 | Toda mudança crítica gera registro em `audit_log`                                                               |
| RB-05 | Simplicidade operacional acima de automação completa no MVP                                                     |
| RB-06 | Desenho deve permitir acoplamento futuro com PSP (Asaas, Mercado Pago) sem reescrever lógica de billing interno |
| RB-07 | Confirmações de pagamento e webhooks devem ser idempotentes                                                     |
| RB-08 | Todo dado operacional pertence a um tenant; isolamento por `tenant_id` é obrigatório                           |
| RB-09 | `deposit_amount <= total_price` sempre; violação é erro de validação                                            |
| RB-10 | Valores financeiros snapshot no agendamento; mudança de preço no serviço não afeta agendamentos existentes      |
| RB-11 | O mesmo lembrete não deve ser enviado duas vezes para o mesmo agendamento na mesma janela                       |
| RB-12 | Retries de envio de lembrete têm limite de 3 tentativas                                                         |
| RB-13 | Cancelamento de tenant não destrói dados operacionais automaticamente                                           |

---

## Superfície de API do MVP

### Autenticação
```
POST /auth/login           → JWT token
GET  /auth/me              → usuário autenticado + tenant + billing_status
```

### Admin Global (A1)
```
POST   /admin/tenants                              → UC-01
POST   /admin/tenants/{id}/users                   → UC-02
POST   /admin/tenants/{id}/billing                 → UC-03
POST   /admin/tenants/{id}/billing/payments        → UC-14
POST   /admin/tenants/{id}/cancel                  → UC-15
GET    /admin/tenants                              → listagem
GET    /admin/tenants/{id}                         → detalhe
```

### Operação do Tenant (A2)
```
# Clientes
GET    /customers              → UC-05
POST   /customers              → UC-05
GET    /customers/{id}

# Serviços
GET    /services               → UC-06
POST   /services               → UC-06
GET    /services/{id}

# Agendamentos
GET    /appointments           → listagem com filtros
POST   /appointments           → UC-07
GET    /appointments/{id}
POST   /appointments/{id}/charges/deposit          → UC-08
POST   /appointments/{id}/charges/deposit/confirm  → UC-09
POST   /appointments/{id}/complete                 → UC-11
POST   /appointments/{id}/charges/balance          → UC-12
POST   /appointments/{id}/cancel
```

### Sistema
```
GET /health   → { status: "ok", version: "..." }
```

---

## Jobs e Worker

### `app/jobs/run_due.py` — executado a cada 5 min pelo scheduler
Responsabilidades:
1. Verificar `billing_accounts` com `next_due_date` vencida → atualizar status
2. Disparar `Reminder` com `status = pending` e `scheduled_for <= now` para o worker

### `app/worker.py` — worker assíncrono
Responsabilidades:
1. Consumir fila de envio de lembretes
2. Chamar integração WhatsApp (Meta Cloud API)
3. Atualizar `Reminder.status` e `attempt_count`

---

## Integrações

### WhatsApp — Meta Cloud API
- Variáveis: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`
- No MVP: envio de mensagem de template para lembrete de atendimento
- Webhook para status de entrega: registrar em `Reminder.status`
- Falhas: registrar em `Reminder.last_error`, retry até 3x

### Pix
- No MVP: cobrança é **manual** — o admin confirma o recebimento pela UI (UC-09)
- Variáveis `PIX_PROVIDER_API_KEY` e `PIX_PROVIDER_WEBHOOK_SECRET` estão reservadas para integração futura (Asaas ou equivalente)
- A entidade `Charge` já tem `external_ref` e `expires_at` para suportar integração sem migration destrutiva

---

## Fora do Escopo do MVP

- Integração Pix automática com webhook (pagamento confirmado manualmente)
- Chatbot com IA
- Emissão fiscal
- CRM completo
- Conciliação financeira
- Multi-unidade complexa
- App mobile nativo
- Frontend (o MVP entrega apenas a API)

---

## Casos de Uso por Prioridade de Implementação

| Prioridade | UC    | Descrição                              |
|------------|-------|----------------------------------------|
| 1          | UC-01 | Criar tenant                           |
| 1          | UC-02 | Criar usuário inicial                  |
| 1          | UC-03 | Configurar billing                     |
| 1          | UC-04 | Login do usuário                       |
| 2          | UC-05 | Cadastrar cliente final                |
| 2          | UC-06 | Cadastrar serviço                      |
| 2          | UC-07 | Criar agendamento                      |
| 2          | UC-08 | Gerar cobrança de sinal                |
| 2          | UC-09 | Confirmar pagamento manualmente        |
| 3          | UC-10 | Enviar lembrete via WhatsApp           |
| 3          | UC-11 | Concluir atendimento                   |
| 3          | UC-12 | Gerar cobrança de saldo                |
| 4          | UC-13 | Suspender tenant por inadimplência     |
| 4          | UC-14 | Reativar tenant após pagamento         |
| 4          | UC-15 | Cancelar tenant                        |
