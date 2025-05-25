# Changelog

Todas as mudanças importantes deste projeto serão documentadas aqui.

## Beta 0.0.1[2025-05-21]
### Adicionado
- Estrutura unificada com Docker Compose e Dockerfile para deploy automatizado.
- Painel admin integrado ao frontend Dash, com abas para configurações, notificações, banco de dados e inserção de apostas.
- Algoritmo de detecção de surebets (arbitragem esportiva) robusto e modular.
- Integração com Telegram e WhatsApp para notificações em tempo real.
- Banco de dados PostgreSQL com schema otimizado e integração real.
- Sistema de notificações em tempo real (WebSocket, Telegram, WhatsApp).
- Adapters para múltiplas casas de apostas (Bet365, Pinnacle, Betfair, Super Odds) usando padrão Adapter.
- Testes unitários para configurações, segurança e cache.
- Internacionalização do README, badges, changelog separado, licença MIT.
- Scripts de build automatizado (build.sh, build.bat), build.spec para PyInstaller.
- Ponto de entrada unificado (main.py) e script run_surebets.py para execução facilitada.

### Corrigido
- Removida duplicidade de layout no frontend Dash.
- Tokens sensíveis agora são lidos do arquivo de configuração.
- Adicionado psycopg2-binary ao requirements.txt para evitar erros de dependência.
- Limpeza de imports e redundâncias.

### Melhorias Futuras
- Autenticação/admin security no painel admin.
- Expansão das sugestões inteligentes (autocomplete de mercados/bookmakers, histórico mais avançado).
- Melhorias no tratamento de arquivos estáticos e internacionalização do frontend.
- Refatoração para remoção de código legado não utilizado.
- Testes automatizados de integração e cobertura total.

## Beta 0.0.2 [2025-05-24]
### Adicionado
- Nova rota `/api/admin/settings` para leitura e atualização dinâmica das configurações do sistema via painel admin.
- Nova rota `/api/admin/insert-bet` com validação avançada e inserção/busca de eventos no banco de dados.
- Expansão do sistema de internacionalização (novas chaves e textos em português e inglês no frontend e backend).
- Novos campos e melhorias no painel admin para gerenciamento de configurações e apostas.

### Corrigido/Melhorado
- Validação aprimorada de campos obrigatórios na inserção de apostas.
- Ajustes e melhorias nas mensagens de erro e feedback do usuário.
- Pequenas melhorias na estrutura do frontend e integração com backend.

### Removido
- Dependência do `psycopg2-binary` foi removida após migração para `psycopg2` com suporte a `libpq` nativo.
- Código comentado e não utilizado foi removido para limpeza e melhor legibilidade.

## Beta 0.0.3 [2025-05-25]
### Adicionado
- Passo a passo detalhado e visual para geração do executável standalone (.exe) no Windows e Linux, com instruções acessíveis para leigos, emojis, destaques, dicas e sugestões de prints.
- Scripts de build e reparo robustos para Windows (`build/build_windows.cmd`, `build/reparo_python_env.cmd`) e Linux (`build/build_linux.sh`, `build/reparo_python_env.sh`), com detecção automática do Python correto e execução do PyInstaller mesmo em ambientes com múltiplas instalações.
- Orientações para resolução de problemas comuns de PATH, múltiplas instalações de Python e execução do build.
- Internacionalização completa do README: todas as instruções, passo a passo e seções agora disponíveis em português e inglês, lado a lado.

### Corrigido/Melhorado
- README enriquecido com seções visuais, dicas para leigos, prints sugeridos e resumo visual do processo de build e execução.
- Ajustes nos scripts para garantir compatibilidade com Python 3.12+ e ambientes diversos.
- Melhoria na documentação de variáveis de ambiente e estrutura do projeto.

### Removido
- Tornados obsoletos os scripts antigos de build (`build.sh`, `build.bat`), orientando o uso dos novos scripts robustos.
