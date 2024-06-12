from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
import uvicorn
from unstructured.partition.image import partition_image
from unstructured.documents.elements import Element
from unstructured.partition.utils.constants import PartitionStrategy
import io
from PIL import Image
import logging
from typing import List

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

# Inicialização do aplicativo FastAPI
app = FastAPI()

# Configuração de CORS para permitir requisições de qualquer origem
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/imagem/extracoes")
async def extrair_dados_imagem(file: UploadFile = File(...)) -> JSONResponse:
    """
    Extrai dados de uma imagem fornecida pelo usuário.
    
    Args:
        file (UploadFile): Arquivo de imagem para extração.
    
    Returns:
        JSONResponse: Resposta contendo os elementos extraídos da imagem.
    """
    logger.info(f"Recebendo arquivo {file.filename}")
    logger.info(f"Tipo do arquivo: {file.content_type}")

    # Verifica se o arquivo é uma imagem
    if not file.content_type.startswith("image/"):
        logger.warning(f"Arquivo {file.filename} não é uma imagem.")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "O arquivo enviado não é uma imagem.",
                "filename": file.filename,
            },
        )

    try:
        # Extrair os bytes do arquivo de maneira assíncrona e processar a imagem
        img_bytes = await file.read()
        with Image.open(io.BytesIO(img_bytes)) as img:
            image = io.BytesIO()
            img.convert("RGB").save(image, format="JPEG")
            image.seek(0)

        # Extração dos elementos da imagem usando a biblioteca Unstructured
        elements: List[Element] = partition_image(
            file=image,
            languages=["por"],
            strategy=PartitionStrategy.HI_RES,
            infer_table_structure=True,
            hi_res_model_name="yolox",
        )

        resultado = {
            "filename": file.filename,
            "content_type": file.content_type,
            "elements": [element.to_dict() for element in elements],
            "message": "Extração de dados da imagem realizada com sucesso!",
        }

    except Exception as e:
        logger.error(f"Erro ao processar a imagem {file.filename}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a imagem {file.filename}: {e}"
        )

    return JSONResponse(content=resultado)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
