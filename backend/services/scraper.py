from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
import random
import os
import time

USER_AGENTS = [
    # Lista de user-agents populares (desktop e mobile)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

PROXY = os.getenv("SELENIUM_PROXY")  # Exemplo: http://127.0.0.1:8080

class BettingScraper:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        # User-Agent aleatório
        user_agent = random.choice(USER_AGENTS)
        options.add_argument(f'user-agent={user_agent}')
        # Proxy reverso (se definido)
        if PROXY:
            options.add_argument(f'--proxy-server={PROXY}')
        # Outras técnicas antibloqueio
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        # --- Técnicas antibloqueio adicionais ---
        # 1. Janela maximizada (simula usuário real)
        options.add_argument('--start-maximized')
        # 2. Desabilita infobars
        options.add_argument('--disable-infobars')
        # 3. Desabilita extensões
        options.add_argument('--disable-extensions')
        # 4. Desabilita notificações
        options.add_argument('--disable-notifications')
        # 5. Desabilita popups
        options.add_argument('--disable-popup-blocking')
        # 6. Permite cookies
        options.add_argument('--enable-cookies')
        # 7. Desabilita WebRTC (evita vazamento de IP real)
        options.add_argument('--disable-webrtc')
        # 8. Desabilita password manager
        prefs = {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2,
        }
        options.add_experimental_option('prefs', prefs)
        # 9. Delay aleatório entre ações (simula humano)
        self._min_delay = 1.5
        self._max_delay = 3.5
        # 10. Executa como processo único
        options.add_argument('--single-process')
        # 11. Ignora certificados SSL inválidos
        options.add_argument('--ignore-certificate-errors')
        # 12. Remove WebGL vendor (anti-fingerprint)
        # Será aplicado via script após abrir a página
        try:
            self.driver = webdriver.Chrome(options=options)
            # Remover navigator.webdriver
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});\n' +
                          'window.chrome = { runtime: {} };\n' +
                          'Object.defineProperty(navigator, "languages", {get: () => ["pt-BR", "pt"]});\n' +
                          'Object.defineProperty(navigator, "plugins", {get: () => [1,2,3,4,5]});\n' +
                          'const getParameter = WebGLRenderingContext.prototype.getParameter;\n' +
                          'WebGLRenderingContext.prototype.getParameter = function(parameter) {\n' +
                          '  if (parameter === 37445) { return "Intel Inc."; }\n' +
                          '  if (parameter === 37446) { return "Intel Iris OpenGL Engine"; }\n' +
                          '  return getParameter(parameter);\n' +
                          '};'
            })
        except WebDriverException as e:
            raise RuntimeError("ChromeDriver não encontrado ou não está no PATH. Baixe em https://chromedriver.chromium.org/downloads e adicione ao PATH.") from e

    def _human_delay(self):
        import time, random
        time.sleep(random.uniform(self._min_delay, self._max_delay))

    def get_odds_bet365(self, url):
        self.driver.get(url)
        self._human_delay()
        odds_elements = self.driver.find_elements(By.CSS_SELECTOR, '.gl-ParticipantOddsOnly_Odds')
        odds = [el.text for el in odds_elements]
        return odds

    def get_odds_pinnacle(self, url):
        self.driver.get(url)
        self._human_delay()
        odds_elements = self.driver.find_elements(By.CSS_SELECTOR, '.style_odds__3JjGg')
        odds = [el.text for el in odds_elements]
        return odds

    def get_odds_betfair(self, url):
        self.driver.get(url)
        self._human_delay()
        odds_elements = self.driver.find_elements(By.CSS_SELECTOR, '.runner-price')
        odds = [el.text for el in odds_elements]
        return odds

    def get_odds_superodds(self, url):
        self.driver.get(url)
        self._human_delay()
        odds_elements = self.driver.find_elements(By.CSS_SELECTOR, '.odds')
        odds = [el.text for el in odds_elements]
        return odds

    def close(self):
        self.driver.quit()
