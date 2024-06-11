from fastapi import FastAPI, UploadFile
import uvicorn


app = FastAPI()

@app.post("/api/imagem/extracoes")
def extrair_dados_imagem(file: UploadFile):
    """Extrai dados de uma imagem"""
    ...

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port="3000")
