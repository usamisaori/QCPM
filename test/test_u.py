
from qcpm import Circuit

circuit_path = "../data/example_u.qasm"

"""
    params:
        - optimize: Whether to optimize, default: True
        - system: input format, "IBM", "Surface" or "U"
"""
circuit = Circuit(circuit_path, system="IBM", optimize=False)

circuit.save('output', system="U")