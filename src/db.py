# src/db.py

import sqlite3
from pathlib import Path
from typing import Any, Dict


def init_db(db_file: str = "db/simulations.db"):
    """
    Initialize the SQLite database with required tables.
    If the DB file already exists, this will not overwrite it.
    """
    DB_FILE = Path(db_file)
    DB_FILE.parent.mkdir(exist_ok=True)  # ensure db/ folder exists

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Table for each simulation run (use run_id as content_hash)
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS simulation_run (
        run_id TEXT PRIMARY KEY,  -- SHA256 hash of content + timestamp
        task TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # Flattened config parameters
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS simulation_parameters (
        run_id TEXT,
        param_key TEXT,
        param_value TEXT,
        FOREIGN KEY(run_id) REFERENCES simulation_run(run_id)
    )
    """
    )

    # Measurements table
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS measurements (
        run_id TEXT,
        shot INTEGER,
        round INTEGER,
        qubit INTEGER,
        qubit_type TEXT,
        value BOOLEAN,
        coord_x REAL,
        coord_y REAL,
        FOREIGN KEY(run_id) REFERENCES simulation_run(run_id)
    )
    """
    )

    conn.commit()
    conn.close()


def flatten_dict(d: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
    """
    Recursively flatten a nested dictionary.
    e.g., {'parameters': {'distance': 3}} -> {'parameters.distance': 3}
    """
    items: Dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key))
        else:
            items[new_key] = v
    return items


def store_simulation(sim_data: Dict[str, Any], db_file: str = "db/simulations.db", run_id: str | None = None):
    """
    Store simulation data into the DB using run_id (content_hash) as unique identifier.
    """
    if not run_id:
        raise ValueError("run_id (content_hash) must be provided.")

    init_db(db_file)
    DB_FILE = Path(db_file)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 1. Insert simulation run
    task = sim_data["config"].get("task", "unknown")
    c.execute("INSERT OR REPLACE INTO simulation_run (run_id, task) VALUES (?, ?)", (run_id, task))

    # 2. Flatten config and store
    flat_config = flatten_dict(sim_data["config"])
    for k, v in flat_config.items():
        c.execute(
            "INSERT INTO simulation_parameters (run_id, param_key, param_value) VALUES (?, ?, ?)", (run_id, k, str(v))
        )

    # 3. Store measurements
    shots = sim_data["measurements"]["mapped_ordered"]
    for shot_name, shot_data in shots.items():
        shot_no = int(shot_name.split()[1])
        for qubit_type, qubit_list in shot_data.items():
            if isinstance(qubit_list, list):  # ancx, ancz
                for round_data in qubit_list:
                    round_no = round_data["round"]
                    for q in round_data["ord_qubits"]:
                        c.execute(
                            """INSERT INTO measurements
                               (run_id, shot, round, qubit, qubit_type, value, coord_x, coord_y)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                run_id,
                                shot_no,
                                round_no,
                                q["qubit"],
                                q["type"],
                                q["value"],
                                q["coords"][0],
                                q["coords"][1],
                            ),
                        )
            elif isinstance(qubit_list, dict):  # data
                round_data = qubit_list
                for q in round_data["ord_qubits"]:
                    c.execute(
                        """INSERT INTO measurements
                           (run_id, shot, round, qubit, qubit_type, value, coord_x, coord_y)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            run_id,
                            shot_no,
                            1,  # data qubits always round 1
                            q["qubit"],
                            q["type"],
                            q["value"],
                            q["coords"][0],
                            q["coords"][1],
                        ),
                    )

    conn.commit()
    conn.close()
