import pytest

from src.simulator import StimErrorSimulator

test_config: dict = {
    "task": "surface_code:rotated_memory_x",
    "distance": 3,
    "rounds": 2,
    "shots": 1,
    "noise_probs": {
        "after_clifford_depolarization": 0,
        "before_round_data_depolarization": 0,
        "before_measure_flip_probability": 0,
        "after_reset_flip_probability": 0,
    },
}


@pytest.fixture
def stim_seed():
    return 42  # plain Python int, valid for STIM


@pytest.fixture
def simulation():
    return StimErrorSimulator(
        distance=test_config["distance"],
        rounds=test_config["rounds"],
        error_probs=test_config["noise_probs"],
        task=test_config["task"],
    )


TEST_CASE_MEASUREMNT_OUT = [
    False,
    False,
    False,
    False,
    True,
    False,
    True,
    False,
    False,
    False,
    False,
    False,
    True,
    False,
    True,
    False,
    False,
    False,
    False,
    True,
    False,
    False,
    True,
    False,
    False,
]


def test_measurement(simulation, stim_seed):
    # use the fixture value
    measurement_out = simulation.perform_measurement(shots=test_config["shots"], seed=stim_seed)
    assert TEST_CASE_MEASUREMNT_OUT == measurement_out[0].tolist()
