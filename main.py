import os
import sys
import json
import yaml
from src.simulator import Simulator


def load_config(config_path):
    # Check if the config file exists
    if not os.path.exists(config_path):
        print(f"Error: Config file '{config_path}' not found.")
        return None

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


if __name__ == "__main__":
    # Check if a config file argument is provided
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <config_file>")
        sys.exit(1)

    # Get the config file path from command-line arguments
    config_file = sys.argv[1]
    config = load_config(config_file)

    # Parsing the different params from config
    task: str = config["task"]
    distance: int = config["parameters"]["distance"]
    rounds: int = config["parameters"]["rounds"]

    error_prob_dtls: dict = config["parameters"]["errors"]

    export_dtls: dict = config["exports"]
    figure_exporting: bool = export_dtls["figure"]["exporting"]
    figure_file: str = export_dtls["figure"]["file"]
    circuit_exporting: bool = export_dtls["circuit"]["exporting"]
    circuit_file: str = export_dtls["circuit"]["file"]
    output_file: str = export_dtls["output"]["file"]

    # Initialize the simulator
    sim = Simulator(task=task, distance=distance, rounds=rounds, error_probs=error_prob_dtls)

    if figure_exporting:
        sim.draw(figure_file, transparent=False)

    if circuit_exporting:
        sim.export_circ_txt(circuit_file)

    output: dict = {"config": config}

    # Save Output
    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)
