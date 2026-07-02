import os

# CONFIGURAÇÃO DE INFRAESTRUTURA DIRETAMENTE VIA CÓDIGO (SEM .ENV)
# Altere a string abaixo com as suas credenciais fornecidas no painel gratuito da Neon.tech
NEON_DATABASE_URL = "postgresql://usuario:senha@seu-cluster-id.aws.neon.tech/neondb?sslmode=require"

# Caso a string não seja alterada, o sistema usará automaticamente o fallback local para não gerar falhas de execução.
if "seu-cluster-id" in NEON_DATABASE_URL:
    DATABASE_URL = "sqlite:///fallback_local.db"
else:
    DATABASE_URL = NEON_DATABASE_URL

UPLOAD_FOLDER = "images"
LOG_FOLDER = "logs"

# Garante a criação física dos diretórios essenciais
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)