import argparse
import hashlib
import json
import os
import sys
import time

import yaml

from src.simulator import StimErrorSimulator
from src.good_stuff import packing_good_stuff, arranging_good_stuff


def load_config(config_path: str):
    """
    Load a YAML configuration file.
    Raises FileNotFoundError if the file does not exist.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' not found.")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


if __name__ == "__main__":
    # -----------------------------
    # Argument parsing
    # -----------------------------
    parser = argparse.ArgumentParser(
        description="Run NoiseSimulator using a YAML configuration file.", usage="python3 %(prog)s <config.yml>"
    )
    parser.add_argument("config_file", type=str, help="Path to the YAML configuration file.")

    # Parse arguments, show clear message if missing
    if len(sys.argv) < 2:
        parser.print_usage()
        print("Error: Missing config file argument.")
        sys.exit(1)

    args = parser.parse_args()
    config_file = args.config_file

    # -----------------------------
    # Load the config
    # -----------------------------
    try:
        config = load_config(config_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Get the config file path from command-line arguments
    config_file = sys.argv[1]
    config = load_config(config_file)

    # Parsing the different params from config
    task: str = config["task"]
    distance: int = config["parameters"]["distance"]
    rounds: int = config["parameters"]["rounds"]

    shots: int = config["parameters"]["sampling"]["shots"]
    seed: int | None = config["parameters"]["sampling"]["seed"]

    mapping_log: bool = config["parameters"]["mapping"]["console_log"]

    m_printing: bool = config["parameters"]["sampling"]["console_log"]

    error_prob_dtls: dict = config["parameters"]["errors"]

    export_dtls: dict = config["exports"]
    figure_exporting: bool = export_dtls["figure"]["exporting"]
    fig_bg_trans: bool = export_dtls["figure"]["trans_bg"]
    figure_file: str = export_dtls["figure"]["file"]
    circuit_exporting: bool = export_dtls["circuit"]["exporting"]
    circuit_file: str = export_dtls["circuit"]["file"]
    output_file: str = export_dtls["output"]["file"]
    outfile_prettify: bool = export_dtls["output"]["prettify"]

    # Initialize the simulator
    sim = StimErrorSimulator(task=task, distance=distance, rounds=rounds, error_probs=error_prob_dtls)

    if figure_exporting:
        sim.draw(figure_file, transparent=fig_bg_trans)

    if circuit_exporting:
        circ_str: str = sim.export_circ_txt(circuit_file)

    sampling = sim.perform_measurement(shots=shots, seed=seed)

    # For writing in a JSON
    sampling_serializable = [shot.tolist() for shot in sampling]
    if m_printing:
        print(f"\nMeasurement readings:\n{sampling}\nlen: {len(sampling[0])}")
        # print(f"Measurement readings: {sampling_serializable}, len: {len(sampling[0])}")

    # Mapping measurement output
    mapped_measurements_dict = sim.measurement_mapper(sampling_serializable, logging=mapping_log)
    mapped_measurements = mapped_measurements_dict["mapped"]
    mapping_meta = mapped_measurements_dict["meta"]
    # Qubit coordinates
    qubit_coords = sim.get_q_coords()
    # print(type(qubit_coords))
    # print(mapped_measurements)
    packed_good_stuff = packing_good_stuff(mapped_measurements, qubit_coords)
    # print("\n\n", packed_good_stuff)
    big_output = arranging_good_stuff(packed_stuff=packed_good_stuff, rounds=rounds)
    # print(json.dumps(big_output))

    output: dict = {
        "config": config,
        "circuit_text": circ_str,
        "measurements": {
            "raw": sampling_serializable,
            "mapped": [list(item) for item in mapped_measurements],
            "mapped_ordered": big_output,
        },
    }

    # Save output in a JSON
    with open(output_file, "w") as f:
        if outfile_prettify:
            json.dump(output, f, indent=4)
        else:
            json.dump(output, f)

    # ----------------------------
    # Save Output (hash(content+timestamp) file)
    # ----------------------------
    # Serialize deterministically (no pretty print, compact)
    serialized = json.dumps(output, separators=(",", ":")).encode("utf-8")

    # Timestamp string
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Hash of (content + timestamp)
    hash_input = serialized + timestamp.encode("utf-8")
    content_hash = hashlib.sha256(hash_input).hexdigest()[:16]  # use 16 chars for readability

    # Construct filename
    base_dir = os.path.dirname(output_file)
    unique_filename = f"{content_hash}.json"
    unique_filepath = os.path.join(base_dir if base_dir else ".", unique_filename)

    with open(unique_filepath, "w") as f:
        f.write(serialized.decode("utf-8"))
