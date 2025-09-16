import argparse
import hashlib
import json
import os
import sys
import time

import yaml

from src.bitstreamer import bitstreamer
from src.db import store_simulation
from src.good_stuff import arranging_good_stuff, packing_good_stuff
from src.report import generate_report_pdf
from src.simulator import StimErrorSimulator


def load_config(config_path: str):
    """
    Load a YAML configuration file.
    Raises FileNotFoundError if the file does not exist.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' not found.")

    with open(config_path, "r", encoding="utf-8") as file:  # explicit encoding
        config = yaml.safe_load(file)

    return config


if __name__ == "__main__":
    # -----------------------------
    #   Start time
    # -----------------------------
    start_time = time.time()  # Start the timer
    # -----------------------------
    # Argument parsing
    # -----------------------------
    parser = argparse.ArgumentParser(
        description="Run NoiseSimulator using a YAML configuration file.",
        usage="python3 %(prog)s <config.yml>",
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

    # -----------------------------
    # Pre-initialize all config variables
    # -----------------------------

    task: str | None = None
    distance: int | None = None
    rounds: int | None = None

    shots: int | None = None
    seed: int | None = None
    skip_ref_sample: bool = False

    mapping_log: bool = False

    bitstreaming: bool = False
    bitstreaming_fmt: str = "zxd"
    bitstreaming_logging: bool = False

    m_printing: bool = False

    error_prob_dtls: dict | None = None

    export_dtls: dict | None = None
    figure_exporting: bool = False
    fig_bg_trans: bool = False
    figure_file: str = ""
    circuit_exporting: bool = False
    circuit_file: str = ""
    output_file: str = ""
    outfile_prettify: bool = False
    pdf_report: bool = False
    pdf_report_file: str = ""

    circ_str: str | None = None  # was circ_str
    svg_str: str | None = None
    bitstream_str: str | None = None  # was BITSTREAM_STR

    surface_code_fig: str | None = None
    surface_code_file: str = ""
    surface_code_figtype: str = ""

    db_exporting: bool | None = None
    db_file: str = ""

    # -----------------------------
    # Parse config parameters safely
    # -----------------------------
    if config:
        try:
            task = config["task"]
            distance = config["parameters"]["distance"]
            rounds = config["parameters"]["rounds"]

            shots = config["parameters"]["sampling"]["shots"]
            seed = config["parameters"]["sampling"].get("seed", None)
            skip_ref_sample = config["parameters"]["sampling"]["skip_ref_sample"]

            mapping_log = config["parameters"]["mapping"]["console_log"]

            bitstreaming = config["bitstream"]["exporting"]
            bitstreaming_fmt = config["bitstream"]["format"]
            bitstreaming_logging = config["bitstream"]["console_log"]

            m_printing = config["parameters"]["sampling"]["console_log"]

            error_prob_dtls = config["parameters"]["errors"]

            export_dtls = config["exports"]
            # Circuit SVG
            figure_exporting = export_dtls["figure"]["exporting"]
            fig_bg_trans = export_dtls["figure"]["trans_bg"]
            figure_file = export_dtls["figure"]["file"]
            # Circuit text
            circuit_exporting = export_dtls["circuit"]["exporting"]
            circuit_file = export_dtls["circuit"]["file"]
            # JSON
            output_file = export_dtls["output"]["file"]
            outfile_prettify = export_dtls["output"]["prettify"]
            # PDF
            pdf_report = export_dtls["pdf_report"]["exporting"]
            pdf_report_file = export_dtls["pdf_report"]["file"]
            # Database
            db_exporting = export_dtls["database"]["exporting"]
            db_file = export_dtls["database"]["file"]
            # Surface code fig
            surface_code_fig = export_dtls["surface_code_fig"]["exporting"]
            surface_code_file = export_dtls["surface_code_fig"]["file"]
            surface_code_figtype = export_dtls["surface_code_fig"]["type"]

        except KeyError as e:
            raise ValueError(f"Bad config! Missing key in config: {e}")
        except TypeError as e:
            raise ValueError(f"Bad config! Invalid structure in config: {e}")

    # Initialize the simulator
    sim = StimErrorSimulator(task=task, distance=distance, rounds=rounds, error_probs=error_prob_dtls)

    if figure_exporting:
        svg_str = sim.draw(figure_file, transparent=fig_bg_trans)

    if circuit_exporting:
        circ_str = sim.export_circ_txt(circuit_file)

    if surface_code_fig:
        sim.draw_surface_code(surface_code_file, surface_code_figtype)

    sampling = sim.perform_measurement(skip_ref=skip_ref_sample, shots=shots, seed=seed)

    # For writing in a JSON
    sampling_serializable = [shot.tolist() for shot in sampling]
    if m_printing:
        print(f"\nMeasurement readings:\n{sampling}\nlen: {len(sampling[0])}")

    # Mapping measurement output
    mapped_measurements_dict = sim.measurement_mapper(sampling_serializable, logging=mapping_log)
    mapped_measurements = mapped_measurements_dict["mapped"]
    mapping_meta = mapped_measurements_dict["meta"]
    qubit_coords = sim.get_q_coords()
    packed_good_stuff = packing_good_stuff(mapped_measurements, qubit_coords)
    big_output = arranging_good_stuff(packed_stuff=packed_good_stuff, rounds=rounds)

    if bitstreaming:
        mapped_output = big_output
        BITSTREAM_STR = bitstreamer(mapped_output, fmt=bitstreaming_fmt)
        if bitstreaming_logging:
            print(f"\nBitstream with format {bitstreaming_fmt}: \n{BITSTREAM_STR}\n")

    output: dict = {
        "config": config,
        "circuit_text": circ_str,
        "measurements": {
            "raw": sampling_serializable,
            "mapped": [list(item) for item in mapped_measurements],
            "mapped_ordered": big_output,
            "bitstream": BITSTREAM_STR,
        },
    }

    # Save output in a JSON
    with open(output_file, "w", encoding="utf-8") as f:
        if outfile_prettify:
            json.dump(output, f, indent=4)
        else:
            json.dump(output, f)

    # ----------------------------
    # Save Output (hash(content+timestamp) file)
    # ----------------------------
    serialized = json.dumps(output, separators=(",", ":")).encode("utf-8")
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    hash_input = serialized + timestamp.encode("utf-8")
    content_hash = hashlib.sha256(hash_input).hexdigest()[:16]

    base_dir = os.path.dirname(output_file)
    unique_filename = f"{content_hash}.json"
    unique_filepath = os.path.join(base_dir if base_dir else ".", unique_filename)

    with open(unique_filepath, "w", encoding="utf-8") as f:
        f.write(serialized.decode("utf-8"))

    if pdf_report:
        try:
            pdf_dir = os.path.dirname(pdf_report_file)
            if pdf_dir and not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir, exist_ok=True)

            generate_report_pdf(
                json_path=output_file, pdf_path=pdf_report_file, svg_str=svg_str if figure_exporting else None
            )

            print(f"\n✅ PDF report generated: {pdf_report_file}\n")

        except Exception as e:
            print("⚠ PDF Report generation failed.")
            print(f"Reason: {e}")
            print(f"JSON file used: {output_file}")

    if db_exporting:
        db_path = db_file if db_file else "db/simulations.db"
        store_simulation(output, db_file=db_path, run_id=content_hash)

    # -----------------------------
    #   End time
    # -----------------------------
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n⏱ Job finished: {elapsed_time:.2f} seconds")
