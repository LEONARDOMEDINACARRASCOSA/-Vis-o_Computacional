import os
import uuid
from database.connection import SessionLocal
from repositories.analise_repository import AnaliseRepository
from models.analise import AnaliseModel
from services.cv_service import ComputerVisionService
from config.settings import UPLOAD_FOLDER
from typing import List

class MainController:
    def __init__(self):
        self.db = SessionLocal()
        self.repository = AnaliseRepository(self.db)

    def processar_e_salvar(self, image_bytes: bytes) -> AnaliseModel:
        """Orquestra o pipeline de análise, gravação em disco local e persistência no Neon."""
        try:
            # Executa o processamento do Service de Visão Computacional
            metadados = ComputerVisionService.analisar_imagem(image_bytes)
            
            # Gera nome único para o arquivo físico de imagem
            filename = f"captura_{uuid.uuid4().hex}.jpg"
            caminho_final = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(caminho_final, "wb") as f:
                f.write(image_bytes)
            
            # Constrói a entidade de banco de dados
            nova_analise = AnaliseModel(
                image_path=caminho_final,
                descricao=metadados["descricao"],
                objetos=metadados["objetos"],
                quantidade_pessoas=metadados["quantidade_pessoas"],
                rostos=metadados["rostos"],
                idade=metadados["idade"],
                emocao=metadados["emocao"],
                cores=metadados["cores"],
                luminosidade=metadados["luminosidade"],
                nitidez=metadados["nitidez"],
                json_resultado=metadados
            )
            return self.repository.salvar(nova_analise)
        finally:
            self.db.close()

    def obter_historico(self) -> List[AnaliseModel]:
        """Obtém a lista ordenada de registros salvos."""
        try:
            return self.repository.listar_todas()
        finally:
            self.db.close()

    def excluir_registro(self, id_analise: int, caminho_imagem: str) -> bool:
        """Apaga o registro do PostgreSQL Neon e remove o arquivo correspondente do disco."""
        try:
            if os.path.exists(caminho_imagem):
                try:
                    os.remove(caminho_imagem)
                except OSError:
                    pass # Evita travar caso o arquivo já tenha sido removido
            return self.repository.deletar(id_analise)
        finally:
            self.db.close()