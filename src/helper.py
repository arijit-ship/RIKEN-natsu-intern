def chunk_list(lst, chunk_size: int, repeat: int):
    """
    Split lst into 'repeat' chunks of size 'chunk_size'.
    Remaining elements go into a final chunk (if any).
    """
    chunks = []
    start = 0

    # Add 'repeat' chunks
    for _ in range(repeat):
        end = start + chunk_size
        chunks.append(lst[start:end])
        start = end

    # Add remaining elements as last chunk
    if start < len(lst):
        chunks.append(lst[start:])

    return chunks
