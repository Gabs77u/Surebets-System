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
