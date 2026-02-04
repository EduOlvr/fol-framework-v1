from minio import Minio
import io
import numpy as np

class StorageService:
    def __init__(self, bucket_name="pesquisa-multidata"):
        self.client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        self.bucket = bucket_name
        self._criar_bucket_se_nao_existir()

    def _criar_bucket_se_nao_existir(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            print(f"[MINIO] Bucket '{self.bucket}' criado com sucesso.")

    def upload_data(self, filename, data_array):
        """
        Recebe um array, comprime em memória e envia para o MinIO.
        """
        # Cria o arquivo na memória RAM (Buffer)
        buffer = io.BytesIO()
        np.savez_compressed(buffer, data=data_array)
        buffer.seek(0)
        
        tamanho = buffer.getbuffer().nbytes
        
        try:
            self.client.put_object(
                self.bucket,
                filename,
                data=buffer,
                length=tamanho,
                content_type="application/octet-stream"
            )
            return tamanho
        except Exception as e:
            print(f"[ERRO MINIO] Não foi possível enviar: {e}")
            return 0