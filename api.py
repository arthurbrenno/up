from fastapi import FastAPI, UploadFile, File
import uvicorn
from typing import Optional


app = FastAPI()

@app.post("/api/imagem/extracoes")
def extrair_dados_imagem(file: UploadFile = Optional[File]):
    """Extrai dados de uma imagem"""
    if (not isinstance(file, UploadFile)):
        print("Aviso: Arquivo não enviado!")

    return {"exemplo": "deu certo"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=3000)
