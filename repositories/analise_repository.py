from sqlalchemy.orm import Session
from models.analise import AnaliseModel
from typing import List, Optional

class AnaliseRepository:
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, analise: AnaliseModel) -> AnaliseModel:
        """Persiste ou atualiza o registro da análise no banco PostgreSQL Neon."""
        try:
            self.db.add(analise)
            self.db.commit()
            self.db.refresh(analise)
            return analise
        except Exception as e:
            self.db.rollback()
            raise e

    def listar_todas(self) -> List[AnaliseModel]:
        """Recupera todos os registros em ordem decrescente cronológica."""
        return self.db.query(AnaliseModel).order_by(AnaliseModel.created_at.desc()).all()

    def deletar(self, id_analise: int) -> bool:
        """Remove o registro do banco de dados com base no ID primário."""
        analise = self.db.query(AnaliseModel).filter(AnaliseModel.id == id_analise).first()
        if analise:
            try:
                self.db.delete(analise)
                self.db.commit()
                return True
            except Exception as e:
                self.db.rollback()
                raise e
        return False