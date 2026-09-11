from __future__ import annotations
from io import BytesIO
from typing import List, Tuple
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup


def extract_pdf_pages(file_bytes: bytes) -> list[dict]:
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": idx, "text": text})
    return pages


def select_page_range(pages: list[dict], start: int, end: int) -> list[dict]:
    start = max(1, start)
    end = min(len(pages), end)
    return [p for p in pages if start <= p["page"] <= end]


def fetch_url(url: str) -> Tuple[str, str]:
    r = requests.get(url, timeout=20, headers={"User-Agent": "Minds10/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()
    title = (soup.title.get_text(" ", strip=True) if soup.title else url)
    text = soup.get_text("\n", strip=True)
    return title[:300], text[:100000]
