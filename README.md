````markdown
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
task: surface_code
parameters:
  distance: 3
  rounds: 5
  sampling:
    shots: 1000
    seed: 42
  errors:
    depolarizing_prob: 0.01
exports:
  output:
    file: output.json
    prettify: true
  pdf_report:
    exporting: true
    file: report.pdf
```

# YAML Configuration Overview

The following table describes each key in the YAML configuration file for the surface code simulation project.

| **Key** | **Description** | **Example / Notes** |
|---------|-----------------|------------------|
| `task` | Specifies the simulation task to run. | `"surface_code:rotated_memory_z"` <br> Valid options: `"surface_code:rotated_memory_x"`, `"surface_code:rotated_memory_z"` |
| `parameters.distance` | The code distance for the surface code. Must be an **odd integer**. | `3` |
| `parameters.rounds` | Number of syndrome measurement rounds to simulate. | `4` |
| `parameters.errors.after_clifford_depolarization` | Depolarization probability applied after Clifford gates. | `0.0` |
| `parameters.errors.before_round_data_depolarization` | Depolarization probability applied to data qubits **before each round**. | `0.0` |
| `parameters.errors.before_measure_flip_probability` | Probability of flipping a qubit **before measurement**. | `0.0` |
| `parameters.errors.after_reset_flip_probability` | Probability of flipping a qubit **after reset**. | `0.0` |
| `parameters.sampling.seed` | Seed for random number generator; `Null` means random. | `Null` |
| `parameters.sampling.shots` | Number of repetitions (shots) for measurement. | `3` |
| `parameters.sampling.console_log` | Enable logging measurement progress to console. | `True` |
| `parameters.mapping.console_log` | Enable logging qubit mapping steps to console. | `True` |
| `exports.figure.exporting` | Whether to export the simulation figure as SVG. | `True` |
| `exports.figure.trans_bg` | If `True`, generates figure with transparent background. | `False` |
| `exports.figure.type` | Type of figure (optional, currently unused). | *(empty)* |
| `exports.figure.file` | Output file path for the figure. | `"output/new_test_fig.svg"` |
| `exports.circuit.exporting` | Whether to export the generated circuit as text. | `True` |
| `exports.circuit.file` | Output file path for the circuit. | `"output/test_circ.txt"` |
| `exports.output.file` | JSON output file path. | `"output/output.json"` |
| `exports.output.prettify` | Whether to pretty-print JSON output. | `True` |
| `exports.pdf_report.exporting` | Whether to generate a PDF report. | `True` |
| `exports.pdf_report.file` | Output file path for the PDF report. | `"examples/example_report.pdf"` |

### Notes:
- `distance` must always be **odd** for proper surface code simulation.  
- `rounds` determines the number of repeated syndrome measurements.  
- Error probabilities are currently set to `0.0` (ideal noise-free simulation) but can be tuned for realistic simulations.  
- Export paths must exist or will be created by the script.  
- PDF report, circuit text, and SVG figure are optional outputs controlled by the `exports` section.

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

## Acknowledgements

* **RIKEN, Kobe, Japan** – Processor Research Team
* **STIM** – Surface code simulator framework

```
```
