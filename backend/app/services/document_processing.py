from __future__ import annotations

import io
import os
import re
import zipfile


class DocumentProcessingService:
    """Clean and chunk uploaded documents for knowledge retrieval."""

    def process_document(self, content: bytes, filename: str, max_chunk_size: int = 800) -> list[str]:
        text = self.extract_text(content, filename)
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
        return self.chunk_text(cleaned, max_chunk_size=max_chunk_size)

    def extract_text(self, content: bytes, filename: str) -> str:
        lower_name = (filename or "").lower()

        if lower_name.endswith(".docx"):
            return self._extract_docx_text(content)
        if lower_name.endswith(".pdf"):
            return self._extract_pdf_text(content)
        if lower_name.endswith(".txt") or lower_name.endswith(".md"):
            return self._decode_text(content)

        return self._decode_text(content)

    def clean_text(self, text: str) -> str:
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = cleaned.replace("\t", " ")
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n +", "\n", cleaned)
        cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"^[-*•]\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
        return cleaned.strip()

    def chunk_text(self, text: str, max_chunk_size: int = 800) -> list[str]:
        if not text:
            return []

        normalized = text.strip()
        if len(normalized) <= max_chunk_size:
            return [normalized]

        paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n", normalized) if segment.strip()]
        chunks: list[str] = []
        current: list[str] = []
        current_length = 0

        for paragraph in paragraphs:
            if current and current_length + len(paragraph) + 1 > max_chunk_size:
                chunks.append(" ".join(current))
                current = []
                current_length = 0
            current.append(paragraph)
            current_length += len(paragraph) + 1

        if current:
            chunks.append(" ".join(current))

        if chunks:
            return chunks

        sentences = re.split(r"(?<=[.!?])\s+", normalized)
        chunks = []
        current_text = ""
        for sentence in sentences:
            if len(current_text) + len(sentence) + 1 > max_chunk_size and current_text:
                chunks.append(current_text.strip())
                current_text = sentence
            else:
                current_text = f"{current_text} {sentence}".strip()
        if current_text:
            chunks.append(current_text.strip())
        return [chunk for chunk in chunks if chunk]

    def _decode_text(self, content: bytes) -> str:
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    def _extract_docx_text(self, content: bytes) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                if "word/document.xml" not in archive.namelist():
                    return self._decode_text(content)
                xml = archive.read("word/document.xml").decode("utf-8", errors="replace")
                blocks = re.findall(r"<w:t(?: xml:space=\"preserve\")?[^>]*>(.*?)</w:t>", xml)
                if not blocks:
                    return self._decode_text(content)
                return " ".join(self._unescape_xml_text(block) for block in blocks if block.strip())
        except (zipfile.BadZipFile, OSError, ValueError):
            return self._decode_text(content)

    def _extract_pdf_text(self, content: bytes) -> str:
        decoded = self._decode_text(content)
        matches = re.findall(r"\(([^\)]+)\)", decoded)
        if matches:
            text = " ".join(part.strip() for part in matches if part.strip())
            if text:
                return text
        return decoded

    def _unescape_xml_text(self, value: str) -> str:
        value = value.replace("&amp;", "&")
        value = value.replace("&lt;", "<")
        value = value.replace("&gt;", ">")
        value = value.replace("&quot;", '"')
        value = value.replace("&apos;", "'")
        value = value.replace("&#39;", "'")
        return value
