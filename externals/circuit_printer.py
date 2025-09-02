import argparse

import stim
import stimcirq
from cirq.contrib.svg import SVGCircuit

# from IPython.terminal.debugger import TerminalPdb

# ipdb = TerminalPdb()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate error statistics for the rotated surface code")
    parser.add_argument("--distance", type=int, required=True, help="code distance")
    parser.add_argument("--rounds", type=int, required=True, help="measurement rounds")
    parser.add_argument("--repetitions", type=int, required=True, help="number of repetitions")
    parser.add_argument("--error_rate", type=float, required=True, help="error rate")
    parser.add_argument("--meas_error_rate", type=float, required=True, help="measurement error rate")
    parser.add_argument("--seed", type=int, default=20202, help="PRNG seed")
    parser.add_argument("--print", type=bool, default=False, help="print circuit to svg and text file")
    args = parser.parse_args()
    return args


def print_circuits(distance: int, rounds: int, error_rate: float, meas_error_rate: float):
    circuit_phenom = stim.Circuit.generated(
        "surface_code:rotated_memory_x",
        distance=distance,
        rounds=rounds,
        before_round_data_depolarization=error_rate,
        after_reset_flip_probability=0,
        after_clifford_depolarization=0,
        before_measure_flip_probability=meas_error_rate,
    )
    circuit_level = stim.Circuit.generated(
        "surface_code:rotated_memory_x",
        distance=distance,
        rounds=rounds,
        before_round_data_depolarization=error_rate,
        after_reset_flip_probability=error_rate,
        after_clifford_depolarization=error_rate,
        before_measure_flip_probability=meas_error_rate,
    )
    cirq_phenom = stimcirq.stim_circuit_to_cirq_circuit(circuit_phenom)

    svg = SVGCircuit(cirq_phenom)
    svg_data = svg._repr_svg_()

    with open("circuit_phenom.svg", "w") as f:
        f.write(svg_data)

    cirq_level = stimcirq.stim_circuit_to_cirq_circuit(circuit_level)

    svg = SVGCircuit(cirq_level)
    svg_data = svg._repr_svg_()

    with open("circuit_level.svg", "w") as f:
        f.write(svg_data)

    circuit_phenom.to_file("circuit_phenom.txt")
    circuit_level.to_file("circuit_level.txt")


def main():
    args = parse_arguments()

    if args.print:
        print_circuits(
            distance=args.distance, rounds=args.rounds, error_rate=args.error_rate, meas_error_rate=args.meas_error_rate
        )


if __name__ == "__main__":
    main()
