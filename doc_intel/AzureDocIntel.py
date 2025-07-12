from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO
import time
from config.Config import config
from exception import (
    ServiceRequestError,
    HttpResponseError,
    AzureDocIntelException
)


class AzureDocIntel:
    def __init__(self) -> None:
        self.computervision_client = ComputerVisionClient(
            config.AZURE.OCR.ENDPOINT, CognitiveServicesCredentials(config.AZURE.OCR.KEY))

    def ocr_bytes(self, file: bytes) -> str:
        """
        Perform OCR on a file and return extracted plain text.

        :param file: File content in bytes or a BytesIO object
        :return: Extracted plain text from the image or PDF
        :raises AzureDocIntelException: For known OCR failures
        """
        try:
            # Ensure it's a BytesIO stream
            if not isinstance(file, BytesIO):
                file = BytesIO(file)

            # Start OCR using the Read API (supports PDFs and images)
            read_response = self.computervision_client.read_in_stream(
                file, raw=True)
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            # Polling for completion
            while True:
                result = self.computervision_client.get_read_result(
                    operation_id)
                if result.status not in ['notStarted', 'running']:
                    break
                time.sleep(0.5)

            if result.status != OperationStatusCodes.succeeded:
                raise AzureDocIntelException(
                    "OCR processing failed or timed out.")

            # Extract text
            text = ""
            for page_result in result.analyze_result.read_results:
                for line in page_result.lines:
                    text += line.text + "\n"

            return text.strip()

        except Exception as e:
            raise AzureDocIntelException(f"OCR failed: {str(e)}") from e
