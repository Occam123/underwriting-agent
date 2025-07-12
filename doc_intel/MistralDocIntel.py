import base64
import os
from mistralai import Mistral
from config.Config import config
from exceptions import MistralDocIntelException


class MistralDocIntel:
    def __init__(self) -> None:
        self.client = Mistral(api_key=config.MISTRAL.API_KEY)

    def ocr_bytes(self, file: bytes) -> str:
        try:
            base64_pdf = base64.b64encode(file).decode('utf-8')

            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}"
                },
                include_image_base64=True
            )

            return ocr_response

        except Exception as e:
            raise MistralDocIntelException(f"OCR failed: {str(e)}") from e
