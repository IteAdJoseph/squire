# Reminda

SaaS enxuto para **confirmar horários** e **cobrar sinal/saldo via Pix**, com **lembretes no WhatsApp** e operação simples.

## Objetivo

O produto foi desenhado para pequenos negócios que precisam de algo prático para:

- confirmar agendamentos
- reduzir no-show
- cobrar sinal via Pix
- cobrar saldo pendente depois do atendimento
- operar sem planilha, sem ERP e sem fluxo complexo

## Escopo do MVP

O MVP cobre apenas o núcleo operacional:

- cadastro de clientes
- cadastro de serviços
- criação de agendamentos
- geração de cobrança Pix
- confirmação automática por pagamento
- lembrete automático no WhatsApp
- cobrança de saldo pendente
- painel simples de operação

Fica fora do escopo inicial:

- chatbot com IA para atendimento
- emissão fiscal
- CRM completo
- conciliação financeira avançada
- multiunidade complexa
- app mobile nativo

## Stack

### Backend
- FastAPI
- PostgreSQL
- Redis/Valkey
- SQLAlchemy + Alembic

### Processamento assíncrono
- worker dedicado
- scheduler de jobs

### Infra
- Render
- `render.yaml` como fonte de verdade da infraestrutura

### Qualidade
- GitHub Actions para CI
- Dependabot para dependências
- revisão humana obrigatória em mudanças sensíveis

## Estrutura do repositório

```text
repo/
  AGENTS.md
  render.yaml
  backend/
    app/
      main.py
      worker.py
      jobs/
        run_due.py
    requirements.txt
    requirements-dev.txt
    alembic.ini
  .github/
    workflows/
      ci.yml
      redeploy-render.yml
    dependabot.yml