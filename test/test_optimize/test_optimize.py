import sys
sys.path.append('../../')

from qcpm import Circuit

print('Load circuit data with optimization: \n')

# load circuit(system: IBM)
circuit_path = 'data_ibm.qasm'
print(f'Try load and optimize <{circuit_path}>: ')
circuit = Circuit(circuit_path, optimize=False)

print(f'Circuit: <{circuit_path}> without optimization:')
print(circuit.info)

print(f'Circuit: <{circuit_path}> after optimization:')
circuit.optimize() # do optimization
print(circuit.info)

circuit.save('data_ibm_after.qasm')


print('-' * 50 + '\n')


# load circuit(system: Surface)
circuit_path = 'data_surface.qasm'
print(f'Try load and optimize <{circuit_path}>: ')
circuit = Circuit(circuit_path, system='Surface', optimize=False)

print(f'Circuit: <{circuit_path}> without optimization:')
print(circuit.info)

print(f'Circuit: <{circuit_path}> after optimization:')
circuit.optimize() # do optimization
print(circuit.info)

circuit.save('data_surface_after.qasm')