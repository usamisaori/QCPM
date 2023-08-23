from qcpm.circuit import CircuitInfo

circuit_path = '../data/example.qasm'

circuitInfo = CircuitInfo.fromQASM(circuit_path)

print(circuitInfo.SQG)