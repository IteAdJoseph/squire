# AGENTS.md

## Objetivo
Este repositório contém um SaaS enxuto para:
- confirmar horários
- cobrar sinal/saldo via Pix
- enviar lembretes pelo WhatsApp
- operar com o menor número possível de partes móveis

## Princípios
1. Mude o mínimo possível para resolver o problema.
2. Prefira clareza operacional a abstrações “elegantes”.
3. Toda mudança de infra deve passar por `render.yaml`.
4. Toda mudança que afeta fluxo de cobrança, autenticação, webhooks ou banco exige revisão humana.
5. Nunca coloque segredos no código ou em arquivos versionados.

## Fluxo padrão para agentes
1. Leia primeiro:
   - `README.md`
   - `docs/mvp-scope.md`
   - `render.yaml`
   - este `AGENTS.md`
2. Entenda o impacto da mudança.
3. Faça a menor alteração segura.
4. Rode os checks locais.
5. Atualize docs se o comportamento mudou.
6. Abra PR com resumo objetivo, riscos e rollback.

## Tarefas seguras para agentes
- escrever testes
- corrigir bugs isolados
- refatorar módulos pequenos
- melhorar logs, tipagem e validações
- atualizar documentação
- ajustar `render.yaml` quando a infra precisar mudar junto do código

## Tarefas que exigem aprovação humana explícita
- migrations destrutivas
- mudanças em billing/cobrança
- mudanças em autenticação/autorização
- mudanças em webhooks de pagamento ou WhatsApp
- alteração de domínio, DNS, TLS ou segredos
- alteração de planos/custos no Render
- merge em `main`

## Regras de infraestrutura
- use Render Blueprints como fonte de verdade
- não “clique no painel” se a mudança puder estar em `render.yaml`
- não crie um segundo arquivo de infra concorrente
- não duplique configuração entre serviços sem necessidade

## Regras de deploy
- `develop` é integração contínua
- `main` é produção
- deploy automático é feito pelo Render quando os checks passam
- não adicionar deploy em GitHub Actions se o Render já resolve o caso
- o workflow manual de redeploy existe só para emergência

## Estrutura esperada
- `backend/app/main.py` expõe o ASGI app
- `backend/app/worker.py` sobe o worker
- `backend/app/jobs/run_due.py` executa jobs agendados
- `backend/alembic.ini` e migrations controlam schema

## Comandos padrão
### Backend
- instalar deps:
  - `cd backend && python -m pip install -r requirements.txt -r requirements-dev.txt`
- lint:
  - `cd backend && ruff check .`
- format check:
  - `cd backend && ruff format --check .`
- type check:
  - `cd backend && mypy app`
- tests:
  - `cd backend && pytest -q`

### Infra
- validar blueprint:
  - `render blueprints validate render.yaml`

## Convenções de PR
Título:
- `feat: ...`
- `fix: ...`
- `refactor: ...`
- `docs: ...`
- `chore: ...`

Descrição mínima:
- problema
- solução
- risco
- rollback
- evidência de teste

## Checklist antes de abrir PR
- [ ] código compila/roda
- [ ] testes passam
- [ ] lint passa
- [ ] type check passa
- [ ] `render.yaml` continua válido
- [ ] docs atualizadas se necessário
- [ ] nenhum segredo foi adicionado ao repo

## Zonas sensíveis
- qualquer arquivo de webhook
- qualquer migration
- qualquer integração de pagamento
- qualquer integração WhatsApp
- `render.yaml`

## Render + agentes
Quando possível, use:
- Render CLI
- Render skills
- Render MCP

Mas:
- nunca aplique mudanças destrutivas sem revisão humana
- nunca altere secrets em produção por iniciativa própria
- nunca presuma que um redeploy é seguro se houve mudança de schema