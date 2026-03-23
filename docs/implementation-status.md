# Status de Implementação do MVP

> Documento de referência para agentes. Atualizado em 2026-03-23.
> Leia também: `AGENTS.md`, `docs/mvp-scope.md`, `docs/use-cases.md`.

---

## O que foi implementado

### Infra e CI
- `render.yaml` — blueprint completo (web API, worker, cron scheduler, Postgres, Redis/Valkey)
- `.github/workflows/ci.yaml` — ruff, mypy, pytest, validação do render.yaml
- `.github/workflows/redeploy-render.yaml` — redeploy manual de emergência

### Backend — estrutura base
- `backend/app/main.py` — FastAPI app; inclui `auth_router` e `admin_router`; expõe `GET /health`
- `backend/app/config.py` — settings via pydantic-settings; inclui `admin_tenant_slug = "reminda-admin"`
- `backend/app/database.py` — SQLAlchemy engine + `get_db` dependency
- `backend/app/core/security.py` — `hash_password`, `verify_password`, `create_access_token`, `decode_access_token` (PyJWT)
- `backend/alembic/` — migrations rodando; schema atual cobre todos os models abaixo

### Backend — models (`backend/app/models/`)
Todos os models do MVP estão implementados:
- `tenant.py` — `Tenant`
- `user.py` — `User`
- `billing.py` — `BillingAccount`, `BillingPayment`
- `client.py` — `Client` (cliente final do tenant)
- `service.py` — `Service`
- `appointment.py` — `Appointment`
- `charge.py` — `Charge`, `ChargePayment`
- `reminder.py` — `Reminder`
- `audit_log.py` — `AuditLog`
- `enums.py` — todos os enums: `AccessStatus`, `BillingStatus`, `BillingProvider`, `UserRole`, `AppointmentStatus`, `ChargeType`, `ChargeStatus`, `ReminderStatus`

### Backend — autenticação (UC-04)
- `backend/app/auth/router.py` — `POST /auth/login`, `POST /auth/refresh`
- `backend/app/dependencies.py`:
  - `get_current_user` — valida JWT, carrega User
  - `require_active_tenant` — bloqueia `late/suspended/cancelled`; alias `ActiveTenantUser`
  - `require_admin` — verifica `tenant.slug == admin_tenant_slug` AND `role == owner`; alias `AdminUser`

### Backend — endpoints admin (UC-01 a UC-03, UC-14, UC-15)
- `backend/app/admin/router.py` — todos os endpoints do A1 implementados:
  - `POST /admin/tenants` — UC-01
  - `POST /admin/tenants/{id}/users` — UC-02
  - `POST /admin/tenants/{id}/billing` — UC-03
  - `GET  /admin/tenants` — listagem
  - `GET  /admin/tenants/{id}` — detalhe (tenant + user + billing)
  - `POST /admin/tenants/{id}/billing/payments` — UC-14 (pagamento + reativação)
  - `POST /admin/tenants/{id}/cancel` — UC-15
- `backend/app/admin/schemas.py` — schemas Pydantic de entrada/saída

### Testes
- `backend/tests/test_admin_helpers.py` — 12 testes dos helpers `_next_due_date` e `_advance_billing_cycle`

---

## O que ainda falta implementar

### Prioridade alta — endpoints operacionais do tenant (UC-05 a UC-12)

Estes endpoints usam `ActiveTenantUser` como dependência e isolam dados por `tenant_id`.

| UC    | Método + Path                                        | Descrição                                     | Status     |
|-------|------------------------------------------------------|-----------------------------------------------|------------|
| UC-05 | `POST /customers`                                    | Cadastrar cliente final                        | **pendente** |
| UC-05 | `GET  /customers`                                    | Listar clientes do tenant                      | **pendente** |
| UC-05 | `GET  /customers/{id}`                               | Detalhe do cliente                             | **pendente** |
| UC-06 | `POST /services`                                     | Cadastrar serviço                              | **pendente** |
| UC-06 | `GET  /services`                                     | Listar serviços do tenant                      | **pendente** |
| UC-06 | `GET  /services/{id}`                                | Detalhe do serviço                             | **pendente** |
| UC-07 | `POST /appointments`                                 | Criar agendamento (snapshot de valores)        | **pendente** |
| UC-07 | `GET  /appointments`                                 | Listar agendamentos (filtros: status, data)    | **pendente** |
| UC-07 | `GET  /appointments/{id}`                            | Detalhe do agendamento + cobranças             | **pendente** |
| UC-08 | `POST /appointments/{id}/charges/deposit`            | Gerar cobrança de sinal                        | **pendente** |
| UC-09 | `POST /appointments/{id}/charges/deposit/confirm`    | Confirmar pagamento do sinal (→ `confirmed`)   | **pendente** |
| UC-11 | `POST /appointments/{id}/complete`                   | Concluir atendimento (`confirmed` → `completed`) | **pendente** |
| UC-12 | `POST /appointments/{id}/charges/balance`            | Gerar cobrança de saldo                        | **pendente** |
| —     | `POST /appointments/{id}/cancel`                     | Cancelar agendamento                           | **pendente** |

**Regras críticas para esta camada:**
- `deposit_amount <= total_price` (RB-09); erro de validação caso contrário
- Valores financeiros são snapshot no momento da criação do agendamento (RB-10)
- Se `deposit_amount == 0`: status inicial do agendamento = `confirmed` (sem etapa de cobrança de sinal)
- Se `deposit_amount > 0`: status inicial = `awaiting_deposit`; só vai para `confirmed` após UC-09
- Transições de status devem seguir a state machine em `docs/mvp-scope.md`
- Toda transição de estado crítica deve gerar `AuditLog`
- Idempotência em UC-09: não confirmar cobrança já paga (RB-07)

### Prioridade média — jobs e worker (UC-10, UC-13)

| Componente                    | Descrição                                                                   | Status     |
|-------------------------------|-----------------------------------------------------------------------------|------------|
| `app/jobs/run_due.py`         | Job diário: avalia billing vencido → `grace` / `suspended`; dispara reminders | **pendente** |
| `app/worker.py`               | Worker: consome fila de reminders, chama Meta Cloud API, atualiza status    | **pendente** |
| Webhook WhatsApp              | `POST /webhooks/whatsapp` — status de entrega → atualiza `Reminder.status`  | **pendente** |

**Regras críticas para jobs/worker:**
- Job de inadimplência (UC-13): se `next_due_date < today` e dentro de `grace_days` → `grace`; além disso → `suspended` + `access_status = disabled`
- Lembrete não deve ser duplicado para o mesmo agendamento na mesma janela (RB-11)
- Retries têm limite de 3 tentativas (RB-12); após isso, `Reminder.status = failed`
- Webhooks de pagamento e WhatsApp devem ser idempotentes (RB-07)

---

## Detalhes de implementação que o Codex precisa saber

### Tipagem — problema pré-existente nos models
Os models usam `Mapped[sa.Date]` e `Mapped[sa.DateTime]` (tipos SQLAlchemy) em vez de `Mapped[datetime.date]` e `Mapped[datetime]` (tipos Python). O valor em runtime é correto, mas o mypy reclama nas call sites. Padrão adotado: usar `# type: ignore[arg-type]` ou `# type: ignore[assignment]` no router onde necessário. **Não corrija os models** — é uma refatoração de escopo separado.

### Helpers de billing (`backend/app/admin/router.py`)
- `_next_due_date(due_day, *, _today)` — usado apenas em UC-03 (setup inicial). Calcula próximo vencimento a partir de hoje.
- `_advance_billing_cycle(current_due, due_day, *, _today)` — usado apenas em UC-14 (pagamento). Avança mês a mês **em loop** até `next_due > today`. O loop é necessário porque um tenant pode pagar com mais de 1 mês de atraso — avançar só 1 mês geraria período invertido (`period_start > period_end`).

### `require_admin` vs `require_active_tenant`
- `require_admin` (`AdminUser`): para endpoints `/admin/*`. Verifica `tenant.slug == settings.admin_tenant_slug` E `user.role == UserRole.owner`. Não verifica billing.
- `require_active_tenant` (`ActiveTenantUser`): para endpoints operacionais. Verifica `access_status == enabled` E `billing_status not in {late, suspended, cancelled}`.

### Isolamento multi-tenant
Todo endpoint operacional deve filtrar queries com `tenant_id == current_user.tenant_id`. Nunca retornar dados de outro tenant.

### `due_day` validado entre 1–28
O schema valida `1 <= due_day <= 28` para evitar edge cases com meses curtos. Não existe `due_day = 31` no sistema.

---

## Arquivos a criar nos próximos PRs

```
backend/app/operational/          # ou separado por domínio
    router.py                     # endpoints UC-05 a UC-12
    schemas.py                    # schemas Pydantic

backend/app/jobs/
    run_due.py                    # job de inadimplência + disparo de reminders (existe como stub)

backend/app/worker.py             # worker WhatsApp (existe como stub)

backend/app/webhooks/
    router.py                     # POST /webhooks/whatsapp

backend/tests/
    test_operational_*.py         # testes dos endpoints operacionais
```
