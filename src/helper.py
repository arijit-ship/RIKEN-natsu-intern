def chunk_list(lst, chunk_size: int, repeat: int) -> list:
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


def packing_good_stuff(mapped_measurements: list, coordinates: dict) -> list:
    """
    Assign the coordinates to correesponding qubits in mapped measurements.
    """
    packed_stuff_big = []
    packed_per_sample = []
    for measurement in mapped_measurements:
        for item in measurement:
            qubit = item[1]
            coords = coordinates[qubit]
            tem_dict = {"qubit": qubit, "value": item[0], "type": item[2], "coords": coords}
            packed_per_sample.append(tem_dict)
        packed_stuff_big.append(packed_per_sample)

    return packed_stuff_big


def arranging_good_stuff(packed_stuff: list, h: int, w: int) -> list:
    """
    Arrange the good stuff, measuremnts sampling, the qubit label, coordinate, measurment values in a specific orders.
    """
    ...
