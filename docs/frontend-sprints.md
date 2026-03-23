# Frontend — Planejamento de Sprints

> Stack: React 18 + TypeScript + Vite + vite-plugin-pwa
> Repo: `frontend/` na raiz do projeto
> Deploy: Render Static Site
> As sprints são ordenadas para bater com as prioridades de backend já implementadas.

---

## Sprint 0 — Fundação (sem backend novo necessário)

**Objetivo:** projeto funcionando, autenticação completa, shell navegável.

### Setup
- [ ] Inicializar projeto: `npm create vite@latest frontend -- --template react-ts`
- [ ] Instalar dependências base: `react-router-dom`, `axios`, `vite-plugin-pwa`
- [ ] Configurar PWA: manifest, service worker, ícones (nome: Reminda)
- [ ] Configurar proxy de API no Vite para desenvolvimento local
- [ ] Adicionar Render Static Site ao `render.yaml` apontando para `frontend/dist`
- [ ] Adicionar etapa de build frontend no CI (`.github/workflows/ci.yaml`)

### Auth (cobre UC-04)
- [ ] Tela de login — campos: username + senha; tenant identificado pelo username
- [ ] Chamada `POST /auth/login`; armazenar JWT no `localStorage`
- [ ] Interceptor Axios: anexar `Authorization: Bearer <token>` em todas as requisições
- [ ] Interceptor de resposta: redirecionar para login em 401
- [ ] Rota protegida (`<RequireAuth>`) — wraps em todas as páginas autenticadas
- [ ] Logout — limpar token, redirecionar para login

### Shell
- [ ] Layout principal: sidebar/bottom nav + área de conteúdo
- [ ] Navegação: Agenda | Clientes | Serviços | (Admin — visível só para owner do admin tenant)
- [ ] Responsivo: sidebar em desktop, bottom nav em mobile

**Backend necessário:** `POST /auth/login` ✅ (já existe)
**Entrega:** app instalável como PWA, login funcionando, navegação entre telas vazias.

---

## Sprint 1 — Clientes e Serviços (cobre UC-05 e UC-06)

**Objetivo:** o admin consegue cadastrar e listar clientes e serviços.

### Clientes
- [ ] `GET /customers` — lista com nome, telefone, status ativo/inativo
- [ ] Busca local por nome/telefone na listagem
- [ ] Formulário de cadastro: nome (obrigatório), telefone E.164 (obrigatório), notas (opcional)
- [ ] `POST /customers` — cadastrar novo cliente
- [ ] Tela de detalhe do cliente (read-only no MVP)

### Serviços
- [ ] `GET /services` — lista com nome, duração, preço total, valor do sinal
- [ ] Formulário de cadastro: nome, duração (min), preço total, valor do sinal
- [ ] Validação client-side: `deposit_amount <= total_price`
- [ ] `POST /services` — cadastrar novo serviço
- [ ] Tela de detalhe do serviço (read-only no MVP)

**Backend necessário:** `GET/POST /customers`, `GET/POST /services` ✅ (já existe)
**Entrega:** CRUD básico de clientes e serviços funcionando no browser e instalado como PWA.

---

## Sprint 2 — Agendamentos (cobre UC-07)

**Objetivo:** o admin consegue criar e visualizar agendamentos.

### Lista / Dashboard
- [ ] `GET /appointments` — lista filtrada por data (default: hoje)
- [ ] Filtro por status: `all | awaiting_deposit | confirmed | completed | cancelled`
- [ ] Card de agendamento: hora, cliente, serviço, status com cor semântica
- [ ] Navegação entre datas (anterior / próximo / hoje)

### Novo agendamento
- [ ] Formulário: selecionar cliente (autocomplete), selecionar serviço (dropdown)
- [ ] Seletor de data e hora
- [ ] Preview dos valores calculados: total, sinal, saldo
- [ ] `POST /appointments` — criar agendamento
- [ ] Redirecionar para detalhe após criação

### Detalhe do agendamento
- [ ] Exibir: cliente, serviço, horário, status, valores (total / sinal / saldo)
- [ ] Seção de cobranças (vazia por enquanto; preenchida na Sprint 3)
- [ ] Botão cancelar agendamento (`POST /appointments/{id}/cancel`)

**Backend necessário:** `GET/POST /appointments`, `POST /appointments/{id}/cancel` ✅ (já existe)
**Entrega:** fluxo de criação e visualização de agenda funcionando.

---

## Sprint 3 — Cobranças e Conclusão (cobre UC-08, UC-09, UC-11, UC-12)

**Objetivo:** o admin consegue cobrar sinal, confirmar pagamento, concluir e cobrar saldo.

### Cobrança de sinal (UC-08 + UC-09)
- [ ] No detalhe do agendamento com status `awaiting_deposit`:
  - Botão "Gerar cobrança de sinal" → `POST /appointments/{id}/charges/deposit`
  - Exibir cobrança gerada: valor, status `pending`
  - Botão "Confirmar pagamento" → `POST /appointments/{id}/charges/deposit/confirm`
  - Status do agendamento atualiza para `confirmed` após confirmação

### Conclusão (UC-11)
- [ ] No detalhe do agendamento com status `confirmed`:
  - Botão "Concluir atendimento" → `POST /appointments/{id}/complete`
  - Confirmação de ação (modal simples)

### Cobrança de saldo (UC-12)
- [ ] No detalhe do agendamento com status `completed` e `balance_amount > 0`:
  - Botão "Gerar cobrança de saldo" → `POST /appointments/{id}/charges/balance`
  - Exibir cobrança de saldo gerada

**Backend necessário:** `POST /appointments/{id}/charges/*`, `POST /appointments/{id}/complete` ✅ (já existe)
**Entrega:** fluxo financeiro completo — da criação ao recebimento do saldo.

---

## Sprint 4 — Painel Admin (cobre UC-01, UC-02, UC-03, UC-14, UC-15)

**Objetivo:** o dono do SaaS consegue gerenciar tenants pelo frontend.

> Esta tela é visível apenas para usuários do tenant `reminda-admin` com `role = owner`.

### Lista de tenants
- [ ] `GET /admin/tenants` — tabela: nome, slug, status de acesso, status de billing
- [ ] Indicadores visuais de status (ativo, trial, suspenso, cancelado)

### Criar tenant (fluxo guiado)
- [ ] Passo 1: dados do tenant — `POST /admin/tenants`
- [ ] Passo 2: usuário inicial — `POST /admin/tenants/{id}/users`
- [ ] Passo 3: billing — `POST /admin/tenants/{id}/billing`

### Detalhe do tenant
- [ ] `GET /admin/tenants/{id}` — dados do tenant, usuário e billing
- [ ] Registrar pagamento: formulário com valor, data, notas → `POST /admin/tenants/{id}/billing/payments`
- [ ] Cancelar tenant: confirmação → `POST /admin/tenants/{id}/cancel`

**Backend necessário:** todos os endpoints `/admin/*` ✅ (já existem)
**Entrega:** operação completa do SaaS sem precisar de Postman/Swagger.

---

## Sprint 5 — Lembretes e Worker (cobre UC-10, UC-13)

**Objetivo:** visibilidade do status de lembretes; backend de jobs implementado.

> Esta sprint depende do backend de jobs/worker, que ainda não foi implementado.

### Frontend
- [ ] No detalhe do agendamento: seção "Lembretes" com status (`pending | sent | failed`)
- [ ] Exibir `sent_at`, `attempt_count`, `last_error` se houver falha

### Backend (a ser implementado antes desta sprint)
- [ ] `app/jobs/run_due.py` — avalia billing vencido + dispara reminders
- [ ] `app/worker.py` — envia mensagem via Meta Cloud API, atualiza `Reminder.status`
- [ ] `POST /webhooks/whatsapp` — recebe status de entrega da Meta

**Entrega:** ciclo completo de lembrete visível no app.

---

## Convenções do frontend

### Estrutura de pastas
```
frontend/
  src/
    api/          # funções de chamada à API (por recurso)
    components/   # componentes reutilizáveis
    pages/        # uma pasta por tela/rota
    hooks/        # custom hooks (useAuth, useAppointments, etc.)
    types/        # tipos TypeScript espelhando os schemas da API
  public/
    icons/        # ícones para PWA
  index.html
  vite.config.ts
```

### Padrões
- Toda chamada à API fica em `src/api/` — nunca `fetch` direto no componente
- Tipos TypeScript espelham os schemas Pydantic do backend (sem geração automática no MVP)
- Sem biblioteca de UI externa — CSS modules ou Tailwind; sem Material UI, Ant Design, etc.
- Estado global mínimo: só auth no contexto; o restante é local ou via query
- Erros de API exibidos inline, nunca silenciados

### PWA
- `manifest.json`: nome "Reminda", cor primária verde-esmeralda, ícones em 192px e 512px
- Service worker: cache de assets estáticos; sem cache de dados da API (dados devem ser frescos)
- Instalável no Android e iOS (add to home screen)
