import os
import json
import subprocess
import tempfile
import pandas as pd
from io import BytesIO
from helpers import json_dump
from llm.OpenAi import OpenAi, Model
from doc_intel.MistralDocIntel import MistralDocIntel
from helpers import read_system_prompt
from exceptions import DocumentProcessorException
from model.TextRepFile import TextRepFile


class DocumentProcessor:
    def __init__(self):
        self.llm = OpenAi()
        self.doc_intel = MistralDocIntel()

        self.process_map = {
            "pdf": self.process_pdf,
            "xlsx": self.process_xlsx,
            "csv": self.process_csv,
            "doc": self.process_doc,
            "docx": self.process_doc,
            "md": self.process_markdown,
            "txt": self.process_text,
            "json": self.process_json
        }

    def get_file_type(self, filename: str) -> str:
        _, ext = os.path.splitext(filename)
        return ext[1:].lower() if ext else ""

    def process_pdf(self, filename: str, content: bytes) -> dict:
        try:
            result = self.doc_intel.ocr_bytes(content)
            text_content = ""
            for page in result.pages:
                text_content += f"{page.markdown}\n\n"
            return TextRepFile(
                og_type="pdf",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not read pdf: {str(e)}") from e

    def process_xlsx(self, filename: str, content: bytes) -> dict:
        try:
            dfs = pd.read_excel(BytesIO(content), sheet_name=None)
            json_data = {}
            for sheet_name, df in dfs.items():
                json_data[sheet_name] = df.to_dict(orient="records")
            processed_data = {}
            for sheet_name, data in json_data.items():
                content_json = json_dump(data)
                result = self.llm.chat(
                    message=f"File data: '''{content_json}'''",
                    system_message=read_system_prompt("process_xlsx.md"),
                    model=Model.gpt_4_1,
                )
                processed_data[sheet_name] = result[0].content[0].text
            text_content = ""
            for i, (sheet_name, value) in enumerate(processed_data.items()):
                text_content += f"Sheet {i}: {sheet_name}\n"
                text_content += f"-----------------------------\n"
                text_content += f"{value}\n"
            return TextRepFile(
                og_type="xlsx",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not read xlsx: {str(e)}") from e

    def process_csv(self, filename: str, content: bytes) -> dict:
        try:
            df = pd.read_csv(BytesIO(content))
            data = df.to_dict(orient="records")
            content_json = json_dump(data)
            result = self.llm.chat(
                message=f"File data: '''{content_json}'''",
                system_message=read_system_prompt("process_csv.md"),
                model=Model.gpt_4_1,
            )
            text_content = result[0].content[0].text
            return TextRepFile(
                og_type="csv",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not read csv: {str(e)}") from e

    def process_doc(self, filename: str, content: bytes) -> dict:
        try:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in [".doc", ".docx"]:
                raise DocumentProcessorException(
                    f"File must be a .doc or .docx document: {ext}")
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, filename)
                with open(input_path, "wb") as f:
                    f.write(content)
                # Run LibreOffice to convert to PDF in temp dir
                try:
                    subprocess.run([
                        "soffice",
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", tmpdir,
                        input_path
                    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    raise DocumentProcessorException(
                        f"LibreOffice failed: {e.stderr.decode()}") from e
                except FileNotFoundError:
                    raise DocumentProcessorException(
                        "LibreOffice ('soffice') not found. Please install LibreOffice and add it to your PATH.")
                base = os.path.splitext(os.path.basename(filename))[0]
                pdf_path = os.path.join(tmpdir, base + ".pdf")
                if not os.path.exists(pdf_path):
                    raise DocumentProcessorException("Conversion failed; PDF not found.")
                with open(pdf_path, "rb") as f:
                    pdf_content = f.read()
            result = self.doc_intel.ocr_bytes(pdf_content)
            text_content = ""
            for page in result.pages:
                text_content += f"{page.markdown}\n\n"
            return TextRepFile(
                og_type="pdf",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not convert doc to text: {str(e)}") from e

    def process_markdown(self, filename: str, content: bytes) -> dict:
        try:
            text_content = content.decode("utf-8")
            return TextRepFile(
                og_type="md",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not read markdown: {str(e)}") from e

    def process_text(self, filename: str, content: bytes) -> dict:
        try:
            text_content = content.decode("utf-8")
            return TextRepFile(
                og_type="txt",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not read text: {str(e)}") from e

    def process_json(self, filename: str, content: bytes) -> dict:
        try:
            content_obj = json.loads(content.decode("utf-8"))
            text_content = json_dump(content_obj)
            if isinstance(text_content, bytes):
                text_content = text_content.decode("utf-8")
            return TextRepFile(
                og_type="json",
                filename=filename,
                content=text_content
            )
        except Exception as e:
            raise DocumentProcessorException(
                f"Could not read json: {str(e)}") from e

    def document_to_text(self, filename: str, content: bytes) -> dict:
        file_type = self.get_file_type(filename)
        process_function = self.process_map.get(file_type, None)
        if process_function is None:
            raise DocumentProcessorException(
                f"Unsupported file type: {file_type}")
        result = process_function(filename, content)
        return result
