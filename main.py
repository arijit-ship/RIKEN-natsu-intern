import os
import sys
import json
import yaml
from src.simulator import Simulator
"""
Valid tasks are:
"repetition_code:memory"
"surface_code:rotated_memory_x"
"surface_code:rotated_memory_z"
"surface_code:unrotated_memory_x"
"surface_code:unrotated_memory_z"
"color_code:memory_xyz"

"""

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
    error_dtls: dict = config["parameters"]["errors"]
    after_clifford_depolarization: float = error_dtls["after_clifford_depolarization"]
    before_round_data_depolarization: float = error_dtls["before_round_data_depolarization"]
    before_measure_flip_probability: float = error_dtls["before_measure_flip_probability"]  
    after_reset_flip_probability: float = error_dtls["after_reset_flip_probability"]    
    export_dtls: dict = config["exports"]
    figure_exporting: bool = export_dtls["figure"]["exporting"]
    figure_file: str = export_dtls["figure"]["file"]
    circuit_exporting: bool = export_dtls["circuit"]["exporting"]
    circuit_file: str = export_dtls["circuit"]["file"]
    output_file: str = export_dtls["output"]["file"]

    # Initialize the simulator
    sim = Simulator(
        task=task,
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=after_clifford_depolarization,
        before_round_data_depolarization=before_round_data_depolarization,
        before_measure_flip_probability=before_measure_flip_probability,
        after_reset_flip_probability=after_reset_flip_probability
    )

    if figure_exporting:
        sim.draw(figure_file, transparent=False)

    if circuit_exporting:
        sim.export_circ_txt(circuit_file)

    sim.save_output(output_file)

# circ_fig = "output/circuit_fig.svg"
# circ_txt = "output/circuit_text.txt"
# # Example usage:
# sim = Simulator(
#     distance=3,
#     rounds=2,
#     err_prob=0.01,
#     task="surface_code:rotated_memory_z"
# )

# sim.draw(circ_fig, transparent=False)
# sim.export_circ_txt(circ_txt)
