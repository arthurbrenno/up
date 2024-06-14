import os
import subprocess
import platform
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
import uvicorn
from unstructured.partition.image import partition_image
from unstructured.documents.elements import Element
from unstructured.partition.utils.constants import PartitionStrategy
import io
import PIL
import logging
from typing import List
import pytesseract
from typing import Any
from fastapi import Form
from pytesseract import Output

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


def execute_script():
    # Verificar se o sistema operacional é Windows e executar o script PowerShell
    if platform.system() == "Windows":
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        script_path = os.path.join(parent_dir, "upgrade_perms.ps1")
        try:
            # Chamar o PowerShell e forçar a execução do script
            subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    script_path,
                    "-Path",
                    os.path.expandvars("%LOCALAPPDATA%"),
                ],
                check=True,
            )
            logger.info(f"Script PowerShell {script_path} executado com sucesso.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar o script PowerShell: {e}")
            sys.exit(1)


@app.post("/api/imagem/extracoes")
async def extrair_dados_imagem(
    file: UploadFile = File(...), strategy: str = Form(...)
) -> JSONResponse:
    """
    Extrai dados de uma imagem fornecida pelo usuário.

    Args:
        file (UploadFile): Arquivo de imagem para extração.

    Returns:
        JSONResponse: Resposta contendo os elementos extraídos da imagem.
    """

    # SE COMEÇAR A DAR ERRO, COMENTE A LINHA ABAIXO.
    execute_script()

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
        resultado = None
        if strategy == "tesseract":
            resultado = await execute_with_tesseract(img_bytes, file)
        else:
            resultado = await execute_with_unstructured(img_bytes, file)

    except Exception as e:
        logger.error(f"Erro ao processar a imagem {file.filename}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar a imagem {file.filename}: {e}"
        )

    return JSONResponse(content=resultado)


async def execute_with_unstructured(img_bytes: bytes, file: UploadFile) -> dict:
    with PIL.Image.open(io.BytesIO(img_bytes)) as img:
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

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "elements": [element.to_dict() for element in elements],
            "message": "Extração de dados da imagem realizada com sucesso!",
        }


async def execute_with_tesseract(img_bytes: bytes, file: UploadFile) -> Any:
    """Extracts text from an image using Tesseract OCR."""
    # Extract text from the image using Tesseract OCR
    try:
        data = pytesseract.image_to_data(
            PIL.Image.open(io.BytesIO(img_bytes)), lang="por", output_type=Output.DICT
        )
    except Exception as e:
        return {
            "detail": f"Error extracting text from the image {file.filename}: {str(e)}"
        }

    result = []
    for i in range(len(data["text"])):
        if data["text"][i].strip() != "":
            element = {
                "level": data["level"][i],
                "page_num": data["page_num"][i],
                "block_num": data["block_num"][i],
                "par_num": data["par_num"][i],
                "line_num": data["line_num"][i],
                "word_num": data["word_num"][i],
                "left": data["left"][i],
                "top": data["top"][i],
                "width": data["width"][i],
                "height": data["height"][i],
                "conf": data["conf"][i],
                "text": data["text"][i],
            }
            result.append(element)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "elements": result,
        "message": "Text extraction from image successful!",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
