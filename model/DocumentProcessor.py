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

from llm.instance import llm


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
        text_rep_of_doc = process_function(filename, content)

        restructure_documents = False

        if restructure_documents:
            result = llm.chat(
                message=text_rep_of_doc.content,
                system_message="""
                    You are an AI assistant specialized in structuring file content for insurance underwriting workflows.

    You receive raw, unstructured text representations of documents, which may come from PDFs, Markdown files, Excel (XLSX), CSVs, or other sources.

    Your task:

    Structure this content clearly and accessibly in Markdown format.

    Preserve all original data word-for-word; do not omit, paraphrase, or summarize anything.

    Organize the content for readability:

    Use headings for file names or logical sections.

    Render tables using Markdown table syntax when the content is tabular (from XLSX/CSV, etc.).

    Use code blocks for preserving original formatting or layout (e.g., source code, preformatted text, indented content).

    Clearly indicate file boundaries if multiple files are present (e.g., with “--- Start of [filename] ---” and “--- End of [filename] ---”).

    Do not interpret or analyze the data; only structure and reformat it.

    This is specifically for insurance underwriting, so maintain all policy numbers, clause wordings, schedules, and any formatting as provided.

    Example output for a CSV:

    ### Start of file: schedule.csv  
    | Policy No | Asset   | Sum Insured | Expiry Date |  
    |-----------|---------|-------------|-------------|  
    | 12345     | Office  | 1000000     | 2025-10-01  |  
    | 67890     | Factory | 5000000     | 2025-09-15  |  
    ### End of file: schedule.csv  
    Example output for a PDF (text):

    ### Start of file: Statement_of_Facts.pdf  
    Statement of Facts  
    
    Insured: Acme Corporation  
    Policy No: 12345  
    ...  
    ### End of file: Statement_of_Facts.pdf  
    Remember:

    Copy everything word for word; do not lose any content or structure.

    Only reformat for clarity and Markdown compatibility.

    Never remove, summarize, or interpret the original data.
                """,
                model=Model.gpt_4_1,
            )

            text_rep_of_doc = TextRepFile(
                og_type=text_rep_of_doc.og_type,
                filename=text_rep_of_doc.filename,
                content=result
            )

            
        return text_rep_of_doc
