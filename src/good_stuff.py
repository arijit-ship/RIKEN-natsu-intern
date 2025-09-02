"""
Helper functions.
"""


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
    packed_stuff_big: list = []

    for measurement in mapped_measurements:
        packed_per_sample = []
        for item in measurement:
            qubit = item[1]
            coords = coordinates[qubit]
            tem_dict = {"qubit": qubit, "value": item[0], "type": item[2], "coords": coords}
            packed_per_sample.append(tem_dict)
        packed_stuff_big.append(packed_per_sample)

    return packed_stuff_big


def arranging_good_stuff(packed_stuff: list, rounds: int) -> dict:
    """
    Arrange measurement data based off the coordinates.
    """
    BIG_SORTED_RESULTS: dict = {}
    shots: int = 1
    # print(packed_stuff)
    for item_per_shot in packed_stuff:
        # print(item_per_shot)
        # Separate items per type for this shot only
        x_anc_list = [q for q in item_per_shot if q["type"] == "ancx"]
        z_anc_list = [q for q in item_per_shot if q["type"] == "ancz"]
        data_list = [q for q in item_per_shot if q["type"] == "data"]

        # print(len(x_anc_list))

        # Compute number of qubits per round
        num_per_round_x = len(x_anc_list) // rounds
        num_per_round_z = len(z_anc_list) // rounds

        # Group ancx by round
        x_anc_grouped_by_round = [
            {
                "round": r + 1,
                "ord_qubits": sorted(
                    x_anc_list[i : i + num_per_round_x], key=lambda q: (q["coords"][0], q["coords"][1])
                ),
            }
            for r, i in enumerate(range(0, len(x_anc_list), num_per_round_x))
        ]

        # Group ancz by round
        z_anc_grouped_by_round = [
            {
                "round": r + 1,
                "ord_qubits": sorted(
                    z_anc_list[i : i + num_per_round_z], key=lambda q: (q["coords"][0], q["coords"][1])
                ),
            }
            for r, i in enumerate(range(0, len(z_anc_list), num_per_round_z))
        ]

        # Sort data qubits (no rounds)
        data_sorted = {"ord_qubits": sorted(data_list, key=lambda q: (q["coords"][0], q["coords"][1]))}

        BIG_SORTED_RESULTS[f"shot {shots}"] = {
            "ancx": x_anc_grouped_by_round,
            "ancz": z_anc_grouped_by_round,
            "data": data_sorted,
        }

        shots += 1

    return BIG_SORTED_RESULTS

    # print(f"\n\n{x_anc_rounds_flatten_list}")
    # print(f"\n\n{x_anc_grouped_by_round}")
    # print(f"\n\n{x_anc_grouped_by_round_sorted}")
    # print(f"\n\n{z_anc_grouped_by_round_sorted}")
    # print(f"\n\n{data_grouped_by_round_sorted}")
    # print(f"\n\n\n\n\n BIG RESULT:\n{BIG_SORTED_RESULTS}")
