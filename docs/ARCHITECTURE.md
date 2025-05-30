# 🏗️ Architecture Guide - Surebets System

## Visão Geral

O sistema Surebets foi projetado com arquitetura modular, separação de responsabilidades e foco em escalabilidade, testabilidade e facilidade de manutenção.

---

## 📦 Estrutura de Pastas

```
Surebets-System/
├── backend/
│   ├── apps/         # Aplicações principais (dashboard, admin_api, adapters)
│   ├── core/         # Utilitários centrais (i18n, segurança, logger)
│   ├── services/     # Serviços de negócio (arbitrage, notification)
│   └── database/     # Banco de dados e scripts
├── frontend/         # Interface desktop (Tkinter)
├── config/           # Configurações e variáveis de ambiente
├── docker/           # Dockerfiles e docker-compose
├── src/              # Entry point e dependências
└── docs/             # Documentação
```

---

## 🔗 Padrões Arquiteturais

- **Separation of Concerns**: Cada módulo tem responsabilidade única
- **Dependency Injection**: Facilita testes e manutenção
- **Factory Pattern**: Criação dinâmica de adaptadores
- **Observer Pattern**: Notificações e eventos
- **Strategy Pattern**: Algoritmos de arbitragem intercambiáveis

---

## 🔄 Fluxo de Dados

1. **Coleta de Odds**: Adaptadores buscam dados das casas de apostas
2. **Processamento**: Engine de arbitragem identifica oportunidades
3. **Persistência**: Dados salvos no banco (SQLite ou PostgreSQL)
4. **Exposição**: APIs REST servem dados para dashboard/admin
5. **Notificações**: Sistema envia alertas via e-mail/webhook

---

## 🔒 Segurança

- JWT para autenticação
- Rate limiting nas APIs
- Proteção CSRF e CORS
- Variáveis sensíveis fora do código

---

## 🧪 Testabilidade

- Testes unitários, integração e performance
- Fixtures e mocks para bancos e APIs
- Cobertura de código monitorada

---

## 📈 Escalabilidade

- Suporte a múltiplos adaptadores
- Cache Redis para performance
- Pronto para deploy em containers

---

## 🌍 Internacionalização

- Sistema i18n centralizado
- Suporte PT-BR e EN

---

## 🔗 Referências

- [Documentação Completa](DESENVOLVIMENTO_COMPLETO.md)
- [Roadmap de Produção](PRODUCTION_ROADMAP.md)
