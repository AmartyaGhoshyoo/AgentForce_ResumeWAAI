import os
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import requests
import fitz
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

class ResumeFetcherTool(BaseTool):
    name: str = "resume_fetcher"
    description: str = "Fetch resume text from a PDF URL or Google Drive link."

    def _run(self, url: str) -> str:
        url = self._convert_drive_link(url)
        r = requests.get(url)
        r.raise_for_status()
        pdf_bytes = BytesIO(r.content)

        text = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _convert_drive_link(self, link):
        import re
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", link)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        return link
    
tool=ResumeFetcherTool()
result=tool.run('https://drive.google.com/file/d/1KFS6yMjUsdeOaDMfuo7KAuleK1UGEDwP/view?usp=sharing')
print(result)