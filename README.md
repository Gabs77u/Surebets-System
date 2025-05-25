# 🇧🇷 Surebets System | 🇺🇸 Surebets System

> 🇧🇷 Este projeto está disponível em português e inglês. <br>
> 🇺🇸 This project is available in Portuguese and English.

---

## 🇧🇷 Badges e Status | 🇺🇸 Badges and Status

[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/)

---

## 🇧🇷 Roadmap | 🇺🇸 Roadmap

- [ ] 🇧🇷 Autenticação e controle de acesso ao painel admin (login, permissões, logs de acesso)
      🇺🇸 Authentication and access control for admin panel (login, permissions, access logs)
- [ ] 🇧🇷 Expansão do autocomplete e sugestões inteligentes para mercados/bookmakers (machine learning, histórico, preferências do usuário)
      🇺🇸 Expand autocomplete and smart suggestions for markets/bookmakers (machine learning, history, user preferences)
- [ ] 🇧🇷 Internacionalização completa do frontend/admin (idiomas adicionais, detecção automática de idioma, tradução de notificações)
      🇺🇸 Full internationalization of frontend/admin (additional languages, auto language detection, notification translation)
- [ ] 🇧🇷 Testes de integração e aumento da cobertura de testes (testes end-to-end, mocks de APIs externas, CI/CD)
      🇺🇸 Integration tests and increased test coverage (end-to-end tests, external API mocks, CI/CD)
- [ ] 🇧🇷 Documentação técnica detalhada das APIs e exemplos de uso (Swagger/OpenAPI, exemplos práticos, vídeos tutoriais)
      🇺🇸 Detailed API documentation and usage examples (Swagger/OpenAPI, practical examples, tutorial videos)
- [ ] 🇧🇷 Melhorias na experiência do usuário no frontend (UI/UX, responsividade, dark mode, acessibilidade)
      🇺🇸 Frontend user experience improvements (UI/UX, responsiveness, dark mode, accessibility)
- [ ] 🇧🇷 Integração com novas casas de apostas (novos adapters, suporte a odds asiáticas, mercados exóticos)
      🇺🇸 Integration with new bookmakers (new adapters, Asian odds support, exotic markets)
- [ ] 🇧🇷 Monitoramento e alertas em tempo real mais avançados (painel de logs, alertas customizáveis, integração com e-mail)
      🇺🇸 Advanced real-time monitoring and alerts (log panel, customizable alerts, email integration)
- [ ] 🇧🇷 Deploy automatizado em nuvem (Docker/Kubernetes, scripts de provisionamento, deploy em AWS/GCP/Azure)
      🇺🇸 Automated cloud deployment (Docker/Kubernetes, provisioning scripts, deploy to AWS/GCP/Azure)
- [ ] 🇧🇷 Dashboard de estatísticas e relatórios (análises gráficas, exportação de dados, filtros avançados)
      🇺🇸 Statistics dashboard and reports (graphical analysis, data export, advanced filters)
- [ ] 🇧🇷 Sistema de auditoria e histórico de alterações (log de ações, reversão de operações, rastreabilidade)
      🇺🇸 Audit system and change history (action log, operation rollback, traceability)
- [ ] 🇧🇷 Integração com métodos de pagamento e controle financeiro (PayPal, Pix, relatórios de saldo)
      🇺🇸 Integration with payment methods and financial control (PayPal, Pix, balance reports)
- [ ] 🇧🇷 API pública para desenvolvedores terceiros (documentação, autenticação, limites de uso)
      🇺🇸 Public API for third-party developers (documentation, authentication, usage limits)
- [ ] 🇧🇷 Módulo de notificações push/mobile (PWA, integração com apps móveis)
      🇺🇸 Push/mobile notification module (PWA, mobile app integration)
- [ ] 🇧🇷 Suporte a múltiplos perfis de usuário (admin, operador, visualizador)
      🇺🇸 Support for multiple user profiles (admin, operator, viewer)

---

## 🇧🇷 Visão Geral | 🇺🇸 Overview

🇧🇷 Sistema completo e automatizado para detecção de arbitragem esportiva (surebets), com backend robusto (Dash, Flask, FastAPI, PostgreSQL, notificações, adapters para múltiplas casas de apostas, painel admin) e frontend integrado. Pronto para deploy via Docker ou executável standalone.

🇺🇸 A complete and automated system for sports arbitrage (surebets) detection, with a robust backend (Dash, Flask, FastAPI, PostgreSQL, notifications, adapters for multiple bookmakers, admin panel) and integrated frontend. Ready for deployment via Docker or standalone executable.

---

## 🇧🇷 Funcionalidades Principais | 🇺🇸 Main Features

- 🇧🇷 **Dashboard Web Moderno (Dash):** Visualização em tempo real das oportunidades de arbitragem.
  🇺🇸 **Modern Web Dashboard (Dash):** Real-time visualization of arbitrage opportunities.
- 🇧🇷 **Painel de Administração:** Configurações, notificações, overview do banco de dados e inserção de apostas com automações inteligentes. Agora inclui edição dinâmica de configurações e inserção manual de apostas via painel admin.
  🇺🇸 **Admin Panel:** Settings, notifications, database overview, and bet insertion with smart automations. Now includes dynamic configuration editing and manual bet insertion via admin panel.
- 🇧🇷 **Algoritmo de Detecção de Surebets:** Modular, eficiente e testado.
  🇺🇸 **Surebets Detection Algorithm:** Modular, efficient, and tested.
- 🇧🇷 **Banco de Dados PostgreSQL:** Schema otimizado, integração real, sugestões baseadas em histórico.
  🇺🇸 **PostgreSQL Database:** Optimized schema, real integration, history-based suggestions.
- 🇧🇷 **Sistema de Notificações:** WebSocket, Telegram, WhatsApp (configurável via variáveis de ambiente).
  🇺🇸 **Notification System:** WebSocket, Telegram, WhatsApp (configurable via environment variables).
- 🇧🇷 **Adapters para Bookmakers:** Integração com Bet365, Pinnacle, Betfair, Super Odds (padrão Adapter, fácil expansão).
  🇺🇸 **Bookmaker Adapters:** Integration with Bet365, Pinnacle, Betfair, Super Odds (Adapter pattern, easy expansion).
- 🇧🇷 **Internacionalização:** README, badges, changelog, licença MIT.
  🇺🇸 **Internationalization:** README, badges, changelog, MIT license.
- 🇧🇷 **Automação Avançada:** Sugestões inteligentes, validação, autocomplete e limpeza automática no formulário de apostas.
  🇺🇸 **Advanced Automation:** Smart suggestions, validation, autocomplete, and automatic form cleaning.
- 🇧🇷 **Scripts de Build:** build.sh, build.bat, build.spec para PyInstaller, Dockerfile e docker-compose.yml.
  🇺🇸 **Build Scripts:** build.sh, build.bat, build.spec for PyInstaller, Dockerfile, and docker-compose.yml.
- 🇧🇷 **Testes Unitários:** Para configurações, segurança e cache.
  🇺🇸 **Unit Tests:** For settings, security, and cache.

---

## 🇧🇷 Como Executar o Programa | 🇺🇸 How to Run the Program

### 1. 🇧🇷 Pré-requisitos | 🇺🇸 Prerequisites
- 🇧🇷 Docker e Docker Compose **OU** Python 3.11+ instalado
- 🇺🇸 Docker and Docker Compose **OR** Python 3.11+ installed
- (🇧🇷 Opcional | 🇺🇸 Optional) PostgreSQL local, se não usar Docker | Local PostgreSQL if not using Docker

### 2. 🇧🇷 Executando com Docker (Recomendado) | 🇺🇸 Running with Docker (Recommended)

```bash
# 🇧🇷 No diretório raiz do projeto | 🇺🇸 In the project root directory
bash docker-compose.yml up --build
```

- 🇧🇷 Acesse o painel Dash: [http://localhost:8050](http://localhost:8050)
- 🇺🇸 Access Dash panel: [http://localhost:8050](http://localhost:8050)
- 🇧🇷 Acesse o painel Admin: [http://localhost:5000](http://localhost:5000)
- 🇺🇸 Access Admin panel: [http://localhost:5000](http://localhost:5000)

🇧🇷 O banco PostgreSQL será criado automaticamente (usuário: postgres, senha: postgres, banco: surebets).
🇺🇸 PostgreSQL will be created automatically (user: postgres, password: postgres, db: surebets).

### 3. 🇧🇷 Executando Manualmente (Windows/Linux) | 🇺🇸 Running Manually (Windows/Linux)

```bash
# 🇧🇷 Instale as dependências | 🇺🇸 Install dependencies
pip install -r requirements.txt

# (🇧🇷 Opcional | 🇺🇸 Optional) Suba o PostgreSQL localmente e ajuste a variável POSTGRES_URL em config/settings.py | Start PostgreSQL locally and set POSTGRES_URL in config/settings.py

# 🇧🇷 Inicialize o banco (executado automaticamente pelo main.py) | 🇺🇸 Initialize the database (done automatically by main.py)

# 🇧🇷 Execute o sistema | 🇺🇸 Run the system
python main.py
```

- 🇧🇷 Painel Dash: http://localhost:8050
- 🇺🇸 Dash panel: http://localhost:8050
- 🇧🇷 Painel Admin: http://localhost:5000
- 🇺🇸 Admin panel: http://localhost:5000

### 4. 🇧🇷 Gerando Executável Standalone (PyInstaller) | 🇺🇸 Generating Standalone Executable (PyInstaller)

#### Passo a passo detalhado para usuários leigos (Windows)

> ⚡️ **Este guia é para quem não entende nada de tecnologia! Siga cada passo devagar, sem medo.**

---

### 🟢 1. Instale o Python 3.11 ou superior

- 🔗 [Clique aqui para baixar o Python](https://www.python.org/downloads/windows/)
- **Durante a instalação:**
  - Marque a opção **"Add Python to PATH"** (veja a imagem abaixo).
  - Clique em **Install Now**.

> 💡 **Dica:** Se aparecer a tela abaixo, marque a caixa destacada em vermelho antes de instalar!

![Exemplo de instalação do Python com "Add to PATH"](docs/img/python_add_to_path.png)

---

### 🟢 2. Atualize o pip e setuptools

- Aperte `Win + R`, digite `cmd` e pressione **Enter** para abrir o Prompt de Comando.
- Digite o comando abaixo e pressione **Enter**:

```bash
python -m pip install --upgrade pip setuptools
```

> 🖼️ **O que você deve ver:**
> - Linhas mostrando "Successfully installed pip ... setuptools ..."
> - Se aparecer erro de permissão, feche o terminal e abra novamente como administrador (clique com o botão direito e escolha "Executar como administrador").

---

### 🟢 3. Baixe e extraia o projeto Surebets System

- Baixe o arquivo ZIP do projeto.
- Clique com o botão direito e escolha **"Extrair tudo..."**.
- Salve em uma pasta fácil, como **Área de Trabalho**.

> 🖼️ **Sugestão de print:** Mostre a pasta extraída na Área de Trabalho.

---

### 🟢 4. Repare o ambiente Python (caso tenha erros de dependências)

- No Prompt de Comando, digite:

```cmd
build\reparo_python_env.cmd
```

- Aguarde até aparecer "Ambiente reparado com sucesso" ou "All requirements satisfied".

> ⚠️ **Se aparecer erro de permissão,** feche o terminal e abra como administrador.
> 🖼️ **Sugestão de print:** Tela do terminal rodando o script e mostrando as mensagens de sucesso.

---

### 🟢 5. Gere o executável (.exe)

- Ainda no Prompt de Comando, digite:

```cmd
build\build_windows.cmd
```

- O script detecta o Python correto e executa o PyInstaller automaticamente.
- Ao final, aparecerá uma mensagem de sucesso e o arquivo `SurebetsSystem.exe` será criado na sua **Área de Trabalho**.

> 🖼️ **Sugestão de print:** Mostre o arquivo `SurebetsSystem.exe` na Área de Trabalho.

---

### 🟢 6. Execute o sistema

- Dê **dois cliques** em `SurebetsSystem.exe` na Área de Trabalho.
- Se aparecer aviso do Windows SmartScreen ou antivírus:
  - Clique em **"Mais informações"** e depois em **"Executar assim mesmo"**.
  - Se o antivírus bloquear, adicione uma exceção para o arquivo.
- Aguarde alguns segundos. O sistema abrirá dois painéis:
  - Painel Dash: http://localhost:8050
  - Painel Admin: http://localhost:5000

> 🖼️ **Sugestão de print:** Mostre o navegador aberto nos painéis Dash/Admin.

---

### 🟢 7. Dicas rápidas e problemas comuns

- ❗ **Erro de banco de dados?** Verifique se o PostgreSQL está rodando ou use o Docker.
- 🔄 **Sistema não abre?** Reinicie o computador e tente novamente.
- 📦 **Erro "No module named pyinstaller"?** Rode o script de reparo novamente.
- 🔑 **Precisa de senha admin?** Veja em `config/settings.py` ou pergunte ao responsável.
- 🆘 **Suporte:** Envie e-mail para gabrielaraujoseven@gmail.com ou abra uma issue no GitHub.

---

> 🟩 **Resumo visual do processo:**
> 1. ![Ícone Python](docs/img/icon_python.png) Instale o Python
> 2. ![Ícone Terminal](docs/img/icon_terminal.png) Atualize pip/setuptools
> 3. ![Ícone Pasta](docs/img/icon_folder.png) Extraia o projeto
> 4. ![Ícone Ferramenta](docs/img/icon_tools.png) Repare o ambiente
> 5. ![Ícone Build](docs/img/icon_build.png) Gere o executável
> 6. ![Ícone Executar](docs/img/icon_run.png) Execute o sistema
>
> **Dica:** Você pode adicionar prints reais nas pastas `docs/img/` e substituir os exemplos acima para deixar o guia ainda mais visual!

---

## 🇺🇸 Step-by-step guide for non-technical users (Windows)

> ⚡️ **This guide is for those who don't understand anything about technology! Follow each step slowly, don't worry.**

---

### 🟢 1. Install Python 3.11 or higher

- 🔗 [Click here to download Python](https://www.python.org/downloads/windows/)
- **During installation:**
  - Check the option **"Add Python to PATH"** (see image below).
  - Click **Install Now**.

> 💡 **Tip:** If the screen below appears, check the box highlighted in red before installing!

![Example of Python installation with "Add to PATH"](docs/img/python_add_to_path.png)

---

### 🟢 2. Update pip and setuptools

- Press `Win + R`, type `cmd` and press **Enter** to open the Command Prompt.
- Type the command below and press **Enter**:

```bash
python -m pip install --upgrade pip setuptools
```

> 🖼️ **What you should see:**
> - Lines showing "Successfully installed pip ... setuptools ..."
> - If a permission error appears, close the terminal and open it again as administrator (right-click and choose "Run as administrator").

---

### 🟢 3. Download and extract the Surebets System project

- Download the ZIP file of the project.
- Right-click and choose **"Extract all..."**.
- Save it in an easy folder, like **Desktop**.

> 🖼️ **Print suggestion:** Show the extracted folder on the Desktop.

---

### 🟢 4. Repair the Python environment (if you have dependency errors)

- In the Command Prompt, type:

```cmd
build\reparo_python_env.cmd
```

- Wait until "Ambiente reparado com sucesso" or "All requirements satisfied" appears.

> ⚠️ **If a permission error appears,** close the terminal and open as administrator.
> 🖼️ **Print suggestion:** Terminal screen running the script and showing success messages.

---

### 🟢 5. Generate the executable (.exe)

- Still in the Command Prompt, type:

```cmd
build\build_windows.cmd
```

- The script detects the correct Python and runs PyInstaller automatically.
- At the end, a success message will appear and the file `SurebetsSystem.exe` will be created on your **Desktop**.

> 🖼️ **Print suggestion:** Show the file `SurebetsSystem.exe` on the Desktop.

---

### 🟢 6. Run the system

- **Double-click** on `SurebetsSystem.exe` on the Desktop.
- If a Windows SmartScreen or antivirus warning appears:
  - Click **"More info"** and then **"Run anyway"**.
  - If the antivirus blocks, add an exception for the file.
- Wait a few seconds. The system will open two panels:
  - Dash Panel: http://localhost:8050
  - Admin Panel: http://localhost:5000

> 🖼️ **Print suggestion:** Show the browser open on Dash/Admin panels.

---

### 🟢 7. Quick tips and common problems

- ❗ **Database error?** Check if PostgreSQL is running or use Docker.
- 🔄 **System doesn't open?** Restart the computer and try again.
- 📦 **Error "No module named pyinstaller"?** Run the repair script again.
- 🔑 **Need admin password?** Check in `config/settings.py` or ask the responsible person.
- 🆘 **Support:** Email gabrielaraujoseven@gmail.com or open an issue on GitHub.

---

> 🟩 **Visual summary of the process:**
> 1. ![Python Icon](docs/img/icon_python.png) Install Python
> 2. ![Terminal Icon](docs/img/icon_terminal.png) Update pip/setuptools
> 3. ![Folder Icon](docs/img/icon_folder.png) Extract the project
> 4. ![Tools Icon](docs/img/icon_tools.png) Repair the environment
> 5. ![Build Icon](docs/img/icon_build.png) Generate the executable
> 6. ![Run Icon](docs/img/icon_run.png) Run the system
>
> **Tip:** You can add real prints in the `docs/img/` folder and replace the examples above to make the guide even more visual!

---

#### Passo a passo detalhado para usuários leigos (Linux)

> ⚡️ **Este guia é para quem não entende nada de Linux! Siga cada passo devagar, sem medo.**

---

### 🟢 1. Instale o Python 3.11 ou superior

- No Ubuntu/Debian, abra o Terminal (`Ctrl + Alt + T`) e digite:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

- Para outras distribuições, procure por "instalar python3" no Google ou consulte a loja de aplicativos.
- Para verificar se o Python está instalado, digite:

```bash
python3 --version
```

> 🖼️ **O que você deve ver:** Algo como `Python 3.11.8` ou superior.

---

### 🟢 2. Atualize o pip e setuptools

- No Terminal, digite:

```bash
python3 -m pip install --upgrade pip setuptools
```

> 🖼️ **O que você deve ver:** Linhas mostrando "Successfully installed pip ... setuptools ...".
> Se aparecer erro de permissão, adicione `--user` ao comando:
> 
> ```bash
> python3 -m pip install --upgrade pip setuptools --user
> ```

---

### 🟢 3. Baixe e extraia o projeto Surebets System

- Baixe o arquivo ZIP do projeto pelo navegador.
- Clique com o botão direito e escolha **"Extrair aqui"** ou use o comando:

```bash
unzip Surebets-System-main.zip
```

- Entre na pasta extraída:

```bash
cd Surebets-System
```

> 🖼️ **Sugestão de print:** Mostre a pasta aberta no gerenciador de arquivos.

---

### 🟢 4. Repare o ambiente Python (caso tenha erros de dependências)

- No Terminal, digite:

```bash
bash build/reparo_python_env.sh
```

- Aguarde até aparecer "Ambiente reparado com sucesso" ou "All requirements satisfied".

> ⚠️ **Se aparecer erro de permissão,** rode:
> 
> ```bash
> chmod +x build/reparo_python_env.sh
> ./build/reparo_python_env.sh
> ```
> 🖼️ **Sugestão de print:** Tela do terminal rodando o script e mostrando as mensagens de sucesso.

---

### 🟢 5. Gere o executável standalone

- No Terminal, digite:

```bash
bash build/build_linux.sh
```

- O script detecta o Python correto e executa o PyInstaller automaticamente.
- Ao final, aparecerá uma mensagem de sucesso e o arquivo executável será criado na sua pasta **Área de Trabalho** (Desktop) ou na pasta do projeto.

> 🖼️ **Sugestão de print:** Mostre o arquivo executável na Área de Trabalho ou na pasta do projeto.

---

### 🟢 6. Execute o sistema

- Dê **dois cliques** no arquivo gerado ou rode pelo terminal:

```bash
./SurebetsSystem
```

- Se aparecer erro de permissão, rode:

```bash
chmod +x SurebetsSystem
./SurebetsSystem
```

- O sistema abrirá dois painéis:
  - Painel Dash: http://localhost:8050
  - Painel Admin: http://localhost:5000

> 🖼️ **Sugestão de print:** Mostre o navegador aberto nos painéis Dash/Admin.

---

### 🟢 7. Dicas rápidas e problemas comuns

- ❗ **Erro de banco de dados?** Verifique se o PostgreSQL está rodando ou use o Docker.
- 🔄 **Sistema não abre?** Reinicie o computador e tente novamente.
- 📦 **Erro "No module named pyinstaller"?** Rode o script de reparo novamente.
- 🔑 **Precisa de senha admin?** Veja em `config/settings.py` ou pergunte ao responsável.
- 🆘 **Suporte:** Envie e-mail para gabrielaraujoseven@gmail.com ou abra uma issue no GitHub.

---

> 🟩 **Resumo visual do processo:**
> 1. ![Ícone Python](docs/img/icon_python.png) Instale o Python
> 2. ![Ícone Terminal](docs/img/icon_terminal.png) Atualize pip/setuptools
> 3. ![Ícone Pasta](docs/img/icon_folder.png) Extraia o projeto
> 4. ![Ícone Ferramenta](docs/img/icon_tools.png) Repare o ambiente
> 5. ![Ícone Build](docs/img/icon_build.png) Gere o executável
> 6. ![Ícone Executar](docs/img/icon_run.png) Execute o sistema

> **Dica:** Você pode adicionar prints reais nas pastas `docs/img/` e substituir os exemplos acima para deixar o guia ainda mais visual!

---

## 🇺🇸 Step-by-step guide for non-technical users (Linux)

> ⚡️ **This guide is for those who don't understand anything about Linux! Follow each step slowly, don't worry.**

---

### 🟢 1. Install Python 3.11 or higher

- On Ubuntu/Debian, open the Terminal (`Ctrl + Alt + T`) and type:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

- For other distributions, search for "install python3" on Google or check the app store.
- To check if Python is installed, type:

```bash
python3 --version
```

> 🖼️ **What you should see:** Something like `Python 3.11.8` or higher.

---

### 🟢 2. Update pip and setuptools

- In the Terminal, type:

```bash
python3 -m pip install --upgrade pip setuptools
```

> 🖼️ **What you should see:** Lines showing "Successfully installed pip ... setuptools ...".
> If a permission error appears, add `--user` to the command:
> 
> ```bash
> python3 -m pip install --upgrade pip setuptools --user
> ```

---

### 🟢 3. Download and extract the Surebets System project

- Download the ZIP file of the project using the browser.
- Right-click and choose **"Extract here"** or use the command:

```bash
unzip Surebets-System-main.zip
```

- Enter the extracted folder:

```bash
cd Surebets-System
```

> 🖼️ **Print suggestion:** Show the folder open in the file manager.

---

### 🟢 4. Repair the Python environment (if you have dependency errors)

- In the Terminal, type:

```bash
bash build/reparo_python_env.sh
```

- Wait until "Ambiente reparado com sucesso" or "All requirements satisfied" appears.

> ⚠️ **If a permission error appears,** run:
> 
> ```bash
> chmod +x build/reparo_python_env.sh
> ./build/reparo_python_env.sh
> ```
> 🖼️ **Print suggestion:** Terminal screen running the script and showing success messages.

---

### 🟢 5. Generate the standalone executable

- In the Terminal, type:

```bash
bash build/build_linux.sh
```

- The script detects the correct Python and runs PyInstaller automatically.
- At the end, a success message will appear and the executable file will be created on your **Desktop** or in the project folder.

> 🖼️ **Print suggestion:** Show the executable file on the Desktop or in the project folder.

---

### 🟢 6. Run the system

- **Double-click** the generated file or run it from the terminal:

```bash
./SurebetsSystem
```

- If a permission error appears, run:

```bash
chmod +x SurebetsSystem
./SurebetsSystem
```

- The system will open two panels:
  - Dash Panel: http://localhost:8050
  - Admin Panel: http://localhost:5000

> 🖼️ **Print suggestion:** Show the browser open on Dash/Admin panels.

---

### 🟢 7. Quick tips and common problems

- ❗ **Database error?** Check if PostgreSQL is running or use Docker.
- 🔄 **System doesn't open?** Restart the computer and try again.
- 📦 **Error "No module named pyinstaller"?** Run the repair script again.
- 🔑 **Need admin password?** Check in `config/settings.py` or ask the responsible person.
- 🆘 **Support:** Email gabrielaraujoseven@gmail.com or open an issue on GitHub.

---

> 🟩 **Visual summary of the process:**
> 1. ![Python Icon](docs/img/icon_python.png) Install Python
> 2. ![Terminal Icon](docs/img/icon_terminal.png) Update pip/setuptools
> 3. ![Folder Icon](docs/img/icon_folder.png) Extract the project
> 4. ![Tools Icon](docs/img/icon_tools.png) Repair the environment
> 5. ![Build Icon](docs/img/icon_build.png) Generate the executable
> 6. ![Run Icon](docs/img/icon_run.png) Run the system

> **Tip:** You can add real prints in the `docs/img/` folder and replace the examples above to make the guide even more visual!

---

## 🇧🇷 Novidades e Melhorias Recentes | 🇺🇸 Recent News and Improvements

- 🇧🇷 Scripts de build e reparo do ambiente separados e robustos para Windows e Linux:
  - `build/build_windows.cmd` e `build/build_linux.sh` para gerar o executável standalone (.exe) na Área de Trabalho.
  - `build/reparo_python_env.cmd` e `build/reparo_python_env.sh` para corrigir automaticamente problemas de dependências e ambiente Python.
- 🇧🇷 Scripts de build agora detectam automaticamente o Python correto e executam o PyInstaller mesmo em ambientes com múltiplas instalações.
- 🇧🇷 Passo a passo detalhado para usuários leigos no README, incluindo dicas para resolver problemas comuns de build e execução.
- 🇧🇷 requirements.txt atualizado para garantir compatibilidade total com Python 3.12+ (numpy, pandas, matplotlib, etc).
- 🇧🇷 Orientações para build e execução facilitada, mesmo para quem não entende de tecnologia.
- 🇧🇷 Correção de redundâncias e simplificação dos scripts antigos (build.sh, build.bat).

🇺🇸 Build and environment repair scripts separated and robust for Windows and Linux:
  - `build/build_windows.cmd` and `build/build_linux.sh` to generate the standalone executable (.exe) on the Desktop.
  - `build/reparo_python_env.cmd` and `build/reparo_python_env.sh` to automatically fix dependency and Python environment issues.
- Build scripts now automatically detect the correct Python and run PyInstaller even in environments with multiple installations.
- Detailed step-by-step for non-technical users in the README, including tips for solving common build and execution problems.
- requirements.txt updated to ensure full compatibility with Python 3.12+ (numpy, pandas, matplotlib, etc).
- Easy build and execution guidance, even for those who don't understand technology.
- Redundancy correction and simplification of old scripts (build.sh, build.bat).

---

## 🇧🇷 Estrutura do Projeto | 🇺🇸 Project Structure

```
Surebets-System/
├── backend/
│   ├── app.py                # 🇧🇷 Painel Dash (frontend) | 🇺🇸 Dash panel (frontend)
│   ├── admin_api.py          # 🇧🇷 API de administração (Flask) | 🇺🇸 Admin API (Flask)
│   ├── api_integrations/     # 🇧🇷 Adapters para casas de apostas | 🇺🇸 Bookmaker adapters
│   ├── arbitrage_calculator/ # 🇧🇷 Algoritmo de detecção de surebets | 🇺🇸 Surebets detection algorithm
│   ├── bookmakers/           # 🇧🇷 Modelos de casas de apostas | 🇺🇸 Bookmaker models
│   ├── database/             # 🇧🇷 Banco de dados e schema | 🇺🇸 Database and schema
│   ├── notification_system/  # 🇧🇷 Notificações (WebSocket, Telegram, WhatsApp) | 🇺🇸 Notifications (WebSocket, Telegram, WhatsApp)
│   └── ...
├── config/                   # 🇧🇷 Configurações e segurança | 🇺🇸 Settings and security
├── frontend/                 # 🇧🇷 (Opcional) arquivos estáticos/templates | 🇺🇸 (Optional) static/templates
├── tests/                    # 🇧🇷 Testes unitários | 🇺🇸 Unit tests
├── main.py                   # 🇧🇷 Ponto de entrada unificado | 🇺🇸 Unified entry point
├── requirements.txt          # 🇧🇷 Dependências Python | 🇺🇸 Python dependencies
├── Dockerfile                # 🇧🇷 Build Docker | 🇺🇸 Docker build
├── docker-compose.yml        # 🇧🇷 Orquestração Docker | 🇺🇸 Docker orchestration
├── README.md                 # 🇧🇷 Este arquivo | 🇺🇸 This file
├── CHANGELOG.md              # 🇧🇷 Histórico de mudanças | 🇺🇸 Changelog
└── LICENSE                   # 🇧🇷 Licença MIT | 🇺🇸 MIT License
```

---

## 🇧🇷 Variáveis de Ambiente Importantes | 🇺🇸 Important Environment Variables

- `POSTGRES_URL` (🇧🇷 ex: postgresql://postgres:postgres@db:5432/surebets | 🇺🇸 e.g.: postgresql://postgres:postgres@db:5432/surebets)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `WHATSAPP_API_URL`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE`
- `SECRET_KEY`

🇧🇷 Essas variáveis podem ser definidas no ambiente ou diretamente em `config/settings.py`.
🇺🇸 These variables can be set in your environment or directly in `config/settings.py`.

---

## 🇧🇷 Testes | 🇺🇸 Tests

🇧🇷 Execute os testes unitários com:
🇺🇸 Run unit tests with:
```bash
pytest tests/
```

---

## 🇧🇷 Funcionalidades Faltantes / Melhorias Futuras | 🇺🇸 Missing Features / Future Improvements

- 🇧🇷 **Autenticação/Admin Security:** Adicionar autenticação e controle de acesso ao painel admin. (0% implementado)
  🇺🇸 **Authentication/Admin Security:** Add authentication and access control to the admin panel. (0% implemented)
- 🇧🇷 **Sugestões Inteligentes Avançadas:** Expandir autocomplete para mercados/bookmakers, histórico mais detalhado. (40% implementado)
  🇺🇸 **Advanced Smart Suggestions:** Expand autocomplete for markets/bookmakers, more detailed history. (40% implemented)
- 🇧🇷 **Melhorias no Frontend:** Internacionalização do painel, tratamento avançado de arquivos estáticos. (60% implementado)
  🇺🇸 **Frontend Improvements:** Panel internationalization, advanced static file handling. (60% implemented)
- 🇧🇷 **Cobertura de Testes:** Testes de integração e cobertura total. (30% cobertura)
  🇺🇸 **Test Coverage:** Integration tests and full coverage. (30% coverage)
- 🇧🇷 **Refatoração:** Remover código legado não utilizado e otimizar módulos. (90% feito)
  🇺🇸 **Refactoring:** Remove unused legacy code and optimize modules. (90% done)
- 🇧🇷 **Documentação Técnica:** Expandir documentação de APIs e exemplos de uso. (50% feito)
  🇺🇸 **Technical Documentation:** Expand API documentation and usage examples. (50% done)

---

## 🇧🇷 Licença | 🇺🇸 License

🇧🇷 MIT License. Veja o arquivo [LICENSE](LICENSE).
🇺🇸 MIT License. See the [LICENSE](LICENSE) file.

---

## 🇧🇷 Contato | 🇺🇸 Contact

🇧🇷 Dúvidas, sugestões ou bugs? Abra uma issue ou envie um e-mail para gabrielaraujoseven@gmail.com
🇺🇸 Questions, suggestions or bugs? Open an issue or email gabrielaraujoseven@gmail.com
