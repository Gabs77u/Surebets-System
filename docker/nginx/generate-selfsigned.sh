# Script para gerar certificados SSL autoassinados para ambiente de testes
# Uso: bash generate-selfsigned.sh

DOMAIN="test.local"
SSL_DIR="$(dirname "$0")/ssl"

mkdir -p "$SSL_DIR"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$SSL_DIR/$DOMAIN.key" \
  -out "$SSL_DIR/$DOMAIN.crt" \
  -subj "/CN=$DOMAIN"

echo "Certificado autoassinado gerado em $SSL_DIR/$DOMAIN.crt e $SSL_DIR/$DOMAIN.key"
