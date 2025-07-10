# database/postgres.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

class NeonConnection:
    def __init__(self):
        # Usa la URL de Neon directamente o desde variables de entorno
        self.connection_url = os.getenv(
            "NEON_DATABASE_URL",
            "postgresql://neondb_owner:npg_z0P4DgirybhU@ep-tiny-butterfly-adnv5vgb-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
        self.engine = None
        self.SessionLocal = None

    def connect(self):
            engine = create_engine(
                self.connection_url,
                # Pooling ajustado para serverless:
                pool_size=2,           # Conexiones mantenidas abiertas (recomendado: 1-3)
                max_overflow=1,        # Conexiones temporales extras (recomendado: 0-2)
                pool_recycle=300,      # Reciclar conexiones cada 5 minutos (antes del timeout de Neon)
                pool_pre_ping=True,    # Verificar conexión antes de usarla
                pool_timeout=30,       # Espera máxima para obtener conexión (segundos)
                connect_args={
                    "connect_timeout": 10,  # Timeout para establecer conexión inicial
                    "keepalives": 1,        # Mantener conexión activa
                    "keepalives_idle": 30,  # Segundos entre keepalives
                    "keepalives_interval": 10,
                }
            )
            return engine

    @contextmanager
    def get_session(self):
        """Proporciona una sesión manejada para Neon."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# Instancia global
neon_connection = NeonConnection()