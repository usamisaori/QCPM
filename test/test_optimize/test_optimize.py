import sys
sys.path.append('../../')

from qcpm import Circuit


originOutput = sys.stdout
print('Load circuit data with optimization: \n')


file = open('optimize_ibm.txt', 'w')
sys.stdout = file

# load circuit(system: IBM)
circuit_path = '../data/data_ibm.qasm'
print(f'Try load and optimize <{circuit_path}>: ')
circuit = Circuit(circuit_path, optimize=False)

print(f'Circuit: <{circuit_path}> without optimization:')
print(circuit.info)

print(f'Circuit: <{circuit_path}> after optimization:')
circuit.optimize() # do optimization
print(circuit.info)

circuit.save('data_ibm_after.qasm')


file = open('optimize_surface.txt', 'w')
sys.stdout = file

# load circuit(system: Surface)
circuit_path = '../data/data_surface.qasm'
print(f'Try load and optimize <{circuit_path}>: ')
circuit = Circuit(circuit_path, system='Surface', optimize=False)

print(f'Circuit: <{circuit_path}> without optimization:')
print(circuit.info)

print(f'Circuit: <{circuit_path}> after optimization:')
circuit.optimize() # do optimization
print(circuit.info)

circuit.save('data_surface_after.qasm')

sys.stdout = originOutput
