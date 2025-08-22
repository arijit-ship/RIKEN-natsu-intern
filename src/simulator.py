import stim
import re


class Simulator:
    def __init__(self, distance: int, rounds: int, error_probs: dict, task: str):
        """
        Initialize the simulator with parameters.
        """
        self.distance = distance
        self.rounds = rounds
        self.error_probs = error_probs
        self.task = task
        self.ec_circuit = None

        after_clifford_depolarization: float = error_probs["after_clifford_depolarization"]
        before_round_data_depolarization: float = error_probs["before_round_data_depolarization"]
        before_measure_flip_probability: float = error_probs["before_measure_flip_probability"]
        after_reset_flip_probability: float = error_probs["after_reset_flip_probability"]
        # Only generate circuit if distance is odd
        if self.is_distance_odd():
            self.ec_circuit = stim.Circuit.generated(
                self.task,  # must be positional
                distance=self.distance,
                rounds=self.rounds,
                after_clifford_depolarization=after_clifford_depolarization,
                before_round_data_depolarization=before_round_data_depolarization,
                before_measure_flip_probability=before_measure_flip_probability,
                after_reset_flip_probability=after_reset_flip_probability,
            )
        else:
            raise ValueError(f"Distance must be odd, got {self.distance}")

    def is_distance_odd(self) -> bool:
        """Check if distance param is odd"""
        return self.distance % 2 != 0

    def construct_ec_circuit(self):
        """Return the error correction circuit."""
        if self.ec_circuit is None:
            raise RuntimeError("Circuit not constructed (distance was even).")
        return self.ec_circuit

    def draw(self, filename: str | None = None, transparent: bool = True):
        """
        Draw the circuit timeline diagram.
        - If filename is given, save as SVG.
        - If not, return the DiagramHelper (nice in Jupyter).
        - If transparent=False, add a white background.
        """
        if self.ec_circuit is None:
            raise RuntimeError("No circuit to draw (distance was even).")

        svg_str = str(self.ec_circuit.diagram("timeline-svg"))

        if not transparent:
            # Add white background <rect> at the top
            svg_open_tag_end = svg_str.find(">") + 1
            viewbox_match = re.search(r'viewBox="([^"]+)"', svg_str)
            if viewbox_match:
                width, height = map(float, viewbox_match.group(1).split()[2:])
                rect_tag = f'<rect width="{width}" height="{height}" fill="white"/>'
                svg_str = svg_str[:svg_open_tag_end] + rect_tag + svg_str[svg_open_tag_end:]

        if filename:
            with open(filename, "w") as f:
                f.write(svg_str)
            return filename
        else:
            return svg_str if not transparent else self.ec_circuit.diagram("timeline-svg")

    def export_circ_txt(self, filename: str | None = None):
        """
        Export the error correction circuit as a human-readable text file.
        - If filename is given, save to that file.
        - If not, return the circuit string.
        """
        if self.ec_circuit is None:
            raise RuntimeError("No circuit to export (distance was even).")

        circ_str = str(self.ec_circuit)  # Get text representation

        if filename:
            with open(filename, "w") as f:
                f.write(circ_str)
            return filename
        else:
            return circ_str
