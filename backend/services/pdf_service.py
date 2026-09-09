from pypdf import PdfReader


def extract_pdf_pages(pdf_path: str):
    """
    Extract text from a PDF page by page.
    """

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text and text.strip():
            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    chunk_overlap: int = 200
):
    """
    Split text into overlapping chunks.
    """

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(start + chunk_size, text_length)

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def create_pdf_chunks(pdf_path: str):
    """
    Extract PDF text and create chunks while preserving page metadata.
    """

    pages = extract_pdf_pages(pdf_path)

    records = []

    chunk_id = 0

    for page_data in pages:

        page_number = page_data["page"]
        text = page_data["text"]

        page_chunks = chunk_text(text)

        for chunk in page_chunks:

            records.append({
                "chunk_id": chunk_id,
                "page": page_number,
                "text": chunk
            })

            chunk_id += 1

    return records