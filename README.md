# Quantum Surface Code Simulation  

**Summer Research Internship Project – RIKEN, Kobe, Japan**  
Processor Research Team

---

## Project Goal
Simulate **surface code circuits** using **STIM** by:  
- Measuring ancilla and data qubits  
- Arranging and labeling qubits for analysis  

---

## Requirements
- Python **3.12.3** or higher  
- Install dependencies:  
```bash
pip install -r requirements.txt
````

---

## YAML Configuration

The project uses a YAML configuration file to set simulation parameters such as:

* Task type
* Distance and rounds
* Sampling options (shots, seed)
* Error probabilities
* Export options (JSON, PDF, circuit, figure)

Example configuration snippet:

```yaml
# Surface code circuit configuration for rotated Z memory.
task: "surface_code:rotated_memory_z"

parameters:
  distance: 3  # Surface code distance (must be odd)
  rounds: 3    # Number of stabilizer measurement rounds
  errors:
    after_clifford_depolarization: 0.0
    before_round_data_depolarization: 0.0
    before_measure_flip_probability: 0.0
    after_reset_flip_probability: 0.0
  sampling:
    seed: 5
    skip_ref_sample: False
    shots: 3
    console_log: True
  mapping:
    console_log: True

bitstream:
  exporting: True
  format: "zxd"
  console_log: True

exports:
  figure:
    exporting: True
    trans_bg: False
    type:
    file: "output/CircuitFigure.svg"
  circuit:
    exporting: True
    file: "output/CircuitText.txt"
  output:
    file: "output/output.json"
    prettify: True
  pdf_report:
    exporting: True
    file: "examples/example_report.pdf"
```

---

# YAML Configuration Overview

| **Key**                                              | **Description**                                                      | **Example / Notes**                                                                                                        |
| ---------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `task`                                               | Specifies the simulation task to run.                                | `"surface_code:rotated_memory_z"` <br> Valid options: `"surface_code:rotated_memory_x"`, `"surface_code:rotated_memory_z"` |
| `parameters.distance`                                | Surface code distance (odd integer).                                 | `3`                                                                                                                        |
| `parameters.rounds`                                  | Number of syndrome measurement rounds.                               | `3`                                                                                                                        |
| `parameters.errors.after_clifford_depolarization`    | Depolarization probability applied after Clifford gates.             | `0.0`                                                                                                                      |
| `parameters.errors.before_round_data_depolarization` | Depolarization probability applied to data qubits before each round. | `0.0`                                                                                                                      |
| `parameters.errors.before_measure_flip_probability`  | Probability of flipping a qubit before measurement.                  | `0.0`                                                                                                                      |
| `parameters.errors.after_reset_flip_probability`     | Probability of flipping a qubit after reset.                         | `0.0`                                                                                                                      |
| `parameters.sampling.seed`                           | Seed for random number generator.                                    | `5`                                                                                                                        |
| `parameters.sampling.skip_ref_sample`                | Skip computing reference sample (report only flips).                 | `False`                                                                                                                    |
| `parameters.sampling.shots`                          | Number of repetitions (shots) for measurement.                       | `3`                                                                                                                        |
| `parameters.sampling.console_log`                    | Enable logging measurement progress.                                 | `True`                                                                                                                     |
| `parameters.mapping.console_log`                     | Enable logging qubit mapping steps.                                  | `True`                                                                                                                     |
| `bitstream.exporting`                                | Export compiled bitstream.                                           | `True`                                                                                                                     |
| `bitstream.format`                                   | Format of exported bitstream.                                        | `"zxd"`                                                                                                                    |
| `bitstream.console_log`                              | Log bitstream export info.                                           | `True`                                                                                                                     |
| `exports.figure.exporting`                           | Export circuit figure as SVG.                                        | `True`                                                                                                                     |
| `exports.figure.trans_bg`                            | Transparent background for figure.                                   | `False`                                                                                                                    |
| `exports.figure.type`                                | Figure type (optional).                                              | *(empty)*                                                                                                                  |
| `exports.figure.file`                                | Output path for figure.                                              | `"output/CircuitFigure.svg"`                                                                                               |
| `exports.circuit.exporting`                          | Export circuit text.                                                 | `True`                                                                                                                     |
| `exports.circuit.file`                               | Output path for circuit text.                                        | `"output/CircuitText.txt"`                                                                                                 |
| `exports.output.file`                                | JSON output file path.                                               | `"output/output.json"`                                                                                                     |
| `exports.output.prettify`                            | Pretty-print JSON output.                                            | `True`                                                                                                                     |
| `exports.pdf_report.exporting`                       | Export PDF report.                                                   | `True`                                                                                                                     |
| `exports.pdf_report.file`                            | Output path for PDF report.                                          | `"examples/example_report.pdf"`                                                                                            |

### Notes:

* `distance` must always be **odd**.
* `rounds` determines the number of repeated syndrome measurements.
* Error probabilities are currently set to `0.0` (ideal, noise-free simulation).
* Export paths must exist or will be created by the script.

---

## Usage

Run the simulator with a YAML configuration file:

```bash
python3 main.py <config.yml>
```

* Output files (JSON, PDF, SVG, etc.) will be generated based on the configuration.

---

## Linting & Formatting

Code quality is maintained using:

* [Flake8](https://flake8.pycqa.org/) – Python linting
* [Black](https://black.readthedocs.io/) – Code formatting
* [isort](https://pycqa.github.io/isort/) – Import sorting

Example usage:

```bash
flake8 src/
black src/
isort src/
```

---

### ⚠️ Cross-Platform Notice

This project has been **tested on Linux (Ubuntu) only**.

While we use Python's `pathlib` for paths and standard libraries where possible, **other operating systems (Windows, macOS) may require adjustments**.

**Recommendations for non-Linux users:**
- Check file paths, especially relative paths like `PDF_CONFIG_PATH`.
- Ensure all required config files (e.g., `pdf.ini`) exist at the expected locations.
- Consider using the `PROJECT_ROOT` environment variable to override paths if needed.


## Acknowledgements

* **RIKEN, Kobe, Japan** – Processor Research Team
* **STIM** – Surface code simulator framework
