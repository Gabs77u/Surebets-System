# Este arquivo README explica como configurar HTTPS/SSL com Nginx para ambiente de testes.

> Para status, roadmap, conquistas e próximos passos, consulte o checklist consolidado em [CHECKLIST_PRODUCAO.md](CHECKLIST_PRODUCAO.md).

## 1. Domínio e certificados centralizados
- Edite `docker/nginx/env_ssl.conf` para alterar o domínio e caminhos dos certificados.

## 2. Gerar certificados autoassinados
Execute:

    bash ./docker/nginx/generate-selfsigned.sh

Os arquivos serão criados em `docker/nginx/ssl/`.

## 3. Configuração do Nginx
- O arquivo `docker/nginx/nginx.conf` já está pronto para proxy reverso e redirecionamento HTTP → HTTPS.
- O Nginx lê o domínio e certificados do arquivo de configuração.

## 4. Subir o ambiente
Execute:

    docker-compose --profile production up -d

## 5. Testar acesso
- Acesse https://test.local (adicione test.local ao seu /etc/hosts apontando para 127.0.0.1).
- O navegador mostrará aviso de certificado autoassinado (normal em ambiente de testes).

## 6. Produção
- Ao migrar para domínio real, gere certificados Let's Encrypt e atualize `env_ssl.conf`.
- Teste o domínio real em https://www.ssllabs.com/ssltest/.
