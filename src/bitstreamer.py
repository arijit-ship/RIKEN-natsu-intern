"""
Thanks to ChatGPT, writing the docstring and implementation was a piece of cake.
This bitstreamer was a last-minute feature.
"""


from typing import Dict


def bitstreamer(mapped_ordered: Dict, fmt: str = "zxd") -> str:
    """
    Generate a bitstream from a nested qubit dictionary.

    Reads the qubit values from a nested Python dictionary (similar to JSON)
    containing multiple shots, ancilla qubits (X and Z), and data qubits.
    The order of the output bitstream is determined by the provided format string.

    Parameters
    ----------
    mapped_ordered : dict
        A nested dictionary with shots as keys. Each shot contains:
        - 'ancx': list of rounds, each with 'ord_qubits' containing X ancilla qubits
        - 'ancz': list of rounds, each with 'ord_qubits' containing Z ancilla qubits
        - 'data': dictionary with 'ord_qubits' containing data qubits
        Each qubit must have a boolean 'value'.

    fmt : str, default "zxd"
        Controls the order of sections in the bitstream:
        - 'z' -> ancz
        - 'x' -> ancx
        - 'd' -> data
        Any combination is allowed, e.g., "xdz".

    Returns
    -------
    str
        A string of '0's and '1's representing the qubit values in the specified order.

    Raises
    ------
    ValueError
        If `fmt` contains characters other than 'x', 'z', or 'd'.
    """

    bitstream = []

    # Map format characters to dictionary keys
    fmt_map = {"x": "ancx", "z": "ancz", "d": "data"}

    # Validate format string
    for f in fmt:
        if f not in fmt_map:
            raise ValueError(f"Invalid format character: {f}. Allowed: 'x', 'z', 'd'.")

    # Iterate through shots in sorted order for consistency
    for shot_name in sorted(mapped_ordered.keys()):
        shot = mapped_ordered[shot_name]

        # Iterate through sections according to the format string
        for f in fmt:
            key = fmt_map[f]
            if key not in shot:
                continue  # Skip missing sections

            if key == "data":
                # Data qubits have no rounds
                for q in shot[key]["ord_qubits"]:
                    bitstream.append("1" if q["value"] else "0")
            else:
                # Ancilla qubits have multiple rounds
                for round_data in shot[key]:
                    for q in round_data["ord_qubits"]:
                        bitstream.append("1" if q["value"] else "0")

    return "".join(bitstream)
