import sys
sys.path.append('../')

from qcpm.circuit import CircuitInfo


circuit_path = './data/example.qasm'
circuitInfo = CircuitInfo.fromQASM(circuit_path)

print('Circuit Info: ', circuitInfo)

print('\nused single qubit gates: ', circuitInfo.SQG)
print('\nused multi qubits gates: ', circuitInfo.MQG)
