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

        # If we reached the end of the text, stop.
        if end == text_length:
            break

        # Move forward while keeping overlap.
        start = end - chunk_overlap

    return chunks