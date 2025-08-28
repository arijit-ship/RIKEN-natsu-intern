import re

import stim

from src.helper import chunk_list


class StimErrorSimulator:
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

    def perform_measurement(self, shots: int, seed: int | None = None):
        """
        Performs measurements for the circuit and prints results round by round.

        The `seed` parameter can be used to reproduce the same results,
        provided the simulation is run on the same machine with the same
        version of Stim.
        """

        if self.ec_circuit is None:
            raise RuntimeError("No circuit to measure (distance was even).")

        # Compile the circuit sampler
        if seed is None:
            # sampler_d = self.ec_circuit.compile_detector_sampler()
            sampler = self.ec_circuit.compile_sampler()
        else:
            # sampler_d = self.ec_circuit.compile_detector_sampler(seed=seed)
            sampler = self.ec_circuit.compile_sampler(seed=seed)

        sampling_result = sampler.sample(shots=shots)

        return sampling_result

        # return {"result": sampling_result, "length": f"{len(sampling_result)}x{len(sampling_result[0])}"}

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
            return circ_str
        else:
            raise ValueError("File name expected")

    def measurement_mapper(self, measurements_out: list, logging: bool):
        """
        Map and label the output measurement.
        """
        circuit = self.ec_circuit
        h_qubits = set()
        mr_qubits = set()
        m_qubits = set()

        d = self.distance
        r = self.rounds

        if len(measurements_out[0]) != r * ((d**2 - 1)) + d**2:
            raise RuntimeError("Inconsistent measurement output length.")
        else:
            if logging:
                print("\n\nMeasurement output length matched successfully! ✅")

        if logging:
            print("\n--- INSTRUCTION ORDER ---")
        for inst in circuit:
            name = inst.name

            if name == "H":
                if logging:
                    targets = [t.value for t in inst.targets_copy()]
                    print(f"Hadamard gate applied to qubits: {targets}")
                h_qubits.update(t.value for t in inst.targets_copy())

            elif name == "MR":
                if logging:
                    targets = [t.value for t in inst.targets_copy()]
                    print(f"Measurement-Reset on qubits: {targets}")
                mr_qubits.update(t.value for t in inst.targets_copy())

            elif name.startswith("M"):  # includes M, MX, MY, MR
                if logging:
                    targets = [t.value for t in inst.targets_copy()]
                    print(f"Measurement '{name}' on qubits: {targets}")
                m_qubits.update(t.value for t in inst.targets_copy())

        if logging:
            print("\n--- MAPPING QUBITS ---")
            # Intersection
            # common = sorted(h_qubits & mr_qubits)
            # Difference
            # h_only = sorted(h_qubits - mr_qubits)
            mr_only = sorted(mr_qubits - h_qubits)
            h_qubits = sorted(h_qubits)
            m_qubits = sorted(m_qubits)
            mr_qubits = sorted(mr_qubits)
            print(f"All measured data qubits: {m_qubits}, len: {len(m_qubits)}")
            print(f"Measurement-Reset qubits: {mr_qubits}, len: {len(mr_qubits)}")
            print(f"Qubits with a preceding Hadamard: {h_qubits}, len: {len(h_qubits)}")
            print(f"Qubits without a Hadamard: {mr_only}, len: {len(mr_only)}")

        chunked = chunk_list(measurements_out[0], len(mr_qubits), repeat=r)

        if logging:
            print(f"\nOriginal measurement output: {measurements_out}")
            print(f"Chunked measurement output: {chunked}")

        intermediate_measurements = chunked[: self.rounds]
        if logging:
            print(f"\nIntermediate ancilla measurements: {intermediate_measurements}")
        final_measurements = chunked[-1]
        if logging:
            print(f"Final measurements on data qubits: {final_measurements}")

        mapped_result: list = []
        for item in intermediate_measurements:
            for i in zip(item, mr_qubits):
                if i[1] in h_qubits:
                    mapped_result.append((*i, "ancx"))
                else:
                    mapped_result.append((*i, "ancz"))

        for i in zip(final_measurements, m_qubits):
            mapped_result.append((*i, "data"))

        if logging:
            print("\n--- MAPPED RESULTS ---")
            print(mapped_result)

        return mapped_result
