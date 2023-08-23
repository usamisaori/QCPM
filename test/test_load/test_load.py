import sys
sys.path.append('../../')

from qcpm import Circuit

print('Load circuit data without optimization: \n')

# load circuit(system: IBM)
circuit_path = 'data_ibm.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path, optimize=False) # default system='IBM'
print(circuit.info)

circuit.save('data_ibm_after.qasm')


# load circuit(system: Surface)
circuit_path = 'data_surface.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path, system='Surface', optimize=False)
print(circuit.info)

circuit.save('data_surface_after.qasm')

