from fastapi import FastAPI, UploadFile
from unstructured.partition.image import partition_image
import uvicorn
import io
import PIL
from typing import List
from unstructured.documents.elements import Element
from unstructured.partition.utils.constants import OCRMode, PartitionStrategy
from pdfminer.utils import open_filename
 #from PIL import Image

app = FastAPI()

@app.post("/api/imagem/extracoes")
async def extrair_dados_imagem(file: UploadFile) -> dict:
    """Extrai dados de uma imagem"""

    # Extrair os bytes do arquivo de maneira assíncrona
    with PIL.Image.open(io.BytesIO(await file.read())) as img:
        image = io.BytesIO()
        img.convert("RGB").save(image, format="JPEG")
        image.seek(0)

    # image = io.BytesIo(await file.read())

    elements: List[Element] = partition_image(
        file=image,
        languages=["por"],
        strategy=PartitionStrategy.HI_RES,
        infer_table_structure=True,
        hi_res_model_name="yolox",
    )

    return {
        "elements": [element.to_dict() for element in elements]
    }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=3000)
