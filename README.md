# Quantum Surface Code Simulation  

**Summer Research Internship Project – RIKEN, Kobe, Japan**  
Processor Research Team

---

## Project Goal
Simulate **surface code circuits** using **STIM** by:  
- Defining and configuring surface code tasks  
- Arranging and labeling qubits for analysis  
- Exporting results (JSON, PDF, circuit figure, surface code figure, bitstream)  

> ⚠️ **Note:** Measurements are no longer stored in the database; only simulation parameters and metadata are recorded.

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
* Sampling options (shots, seed, reference sample)
* Error probabilities
* Export options (JSON, PDF, circuit, figures, database)

Example configuration snippet:

```yaml
task: "surface_code:rotated_memory_z"

parameters:
  distance: 3
  rounds: 2
  errors:
    after_clifford_depolarization: 0.1
    before_round_data_depolarization: 0.1
    before_measure_flip_probability: 0.1
    after_reset_flip_probability: 0.0
  sampling:
    seed: 42
    skip_ref_sample: False
    reference_sample: "auto"
    shots: 2
    console_log: True
  mapping:
    console_log: True

bitstream:
  exporting: True
  format: "zxd"
  console_log: True

exports:
  output:
    file: "output/output.json"
    prettify: True
  figure:
    exporting: True
    trans_bg: False
    type: "timeline-svg"
    file: "output/CircuitFigure.svg"
  surface_code_fig:
    exporting: True
    type: "timeslice-svg"
    file: "output/SurfaceCode.svg"
  circuit:
    exporting: True
    file: "output/CircuitText.txt"
  pdf_report:
    exporting: True
    file: "examples/report_d9.pdf"
  database:
    exporting: True
    file: "db/simulations.db"
```

---

# YAML Configuration Overview

| **Key**                                | **Description**                                      | **Example / Notes**               |
| -------------------------------------- | ---------------------------------------------------- | --------------------------------- |
| `task`                                 | Simulation task to run                               | `"surface_code:rotated_memory_z"` |
| `parameters.distance`                  | Surface code distance (odd integer)                  | `3`                               |
| `parameters.rounds`                    | Number of syndrome measurement rounds                | `2`                               |
| `parameters.errors.*`                  | Error probabilities applied at different stages      | `0.0-0.1` depending on config     |
| `parameters.sampling.seed`             | Random number generator seed                         | `42`                              |
| `parameters.sampling.skip_ref_sample`  | Skip computing reference sample (report only flips)  | `False`                           |
| `parameters.sampling.reference_sample` | Reference sample mode (not implemented yet)          | `"auto"`                          |
| `parameters.sampling.shots`            | Number of repetitions (shots) for measurement        | `2`                               |
| `parameters.sampling.console_log`      | Enable logging measurement progress                  | `True`                            |
| `parameters.mapping.console_log`       | Enable logging qubit mapping steps                   | `True`                            |
| `bitstream.exporting`                  | Export compiled bitstream                            | `True`                            |
| `bitstream.format`                     | Format of exported bitstream                         | `"zxd"`                           |
| `bitstream.console_log`                | Log bitstream export info                            | `True`                            |
| `exports.output.file`                  | JSON output file path                                | `"output/output.json"`            |
| `exports.output.prettify`              | Pretty-print JSON output                             | `True`                            |
| `exports.figure.*`                     | Circuit figure export options                        | `"timeline-svg", file path"`      |
| `exports.surface_code_fig.*`           | Surface code figure export options                   | `"timeslice-svg", file path"`     |
| `exports.circuit.*`                    | Circuit text export options                          | File path                         |
| `exports.pdf_report.*`                 | PDF report export options                            | File path                         |
| `exports.database.*`                   | Database export options (parameters & metadata only) | File path                         |

> ⚠️ **Notes:**
>
> * `distance` must always be **odd**.
> * `rounds` determines the number of repeated syndrome measurements.
> * Error probabilities can now be nonzero for noisy simulations.
> * Export paths must exist or will be created automatically.

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

**Recommendations for non-Linux users:**

* Check file paths carefully (relative paths like `PDF_CONFIG_PATH`).
* Ensure all required config files (e.g., `pdf.ini`) exist at the expected locations.
* Consider using the `PROJECT_ROOT` environment variable to override paths if needed.

---

## Acknowledgements

* **RIKEN, Kobe, Japan** – Processor Research Team
* **STIM** – Surface code simulator framework
