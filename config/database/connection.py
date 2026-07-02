import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import DATABASE_URL, LOG_FOLDER

# Configuração robusta de Logs do Sistema
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_FOLDER, "app.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Compatibilidade estrita de strings de conexão legadas
conn_url = DATABASE_URL
if conn_url.startswith("postgres://"):
    conn_url = conn_url.replace("postgres://", "postgresql://", 1)

# Engine configurada para o ambiente resiliente do Neon (com teste de conexão ativo)
engine = create_engine(conn_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db() -> None:
    """Cria automaticamente as tabelas estruturadas no banco de dados Neon se não existirem."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados sincronizado e tabelas verificadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro crítico ao inicializar as tabelas do banco de dados: {str(e)}")
        raise e