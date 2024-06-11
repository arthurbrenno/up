from fastapi import FastAPI, UploadFile, File
import uvicorn
from typing import Optional


app = FastAPI()

@app.post("/api/imagem/extracoes")
async def extrair_dados_imagem(file: UploadFile):
    """Extrai dados de uma imagem"""

    conteudos: str = await file.read()
    print(conteudos)

    return {"exemplo": "deu certo"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=3000)
