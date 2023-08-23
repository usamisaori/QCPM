import sys
sys.path.append('../../')

from qcpm import Circuit

print('Migration test \n')

# load circuit(system: IBM)
circuit_path = 'data_ibm.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path) # default system='IBM'

circuit.save('data_ibm_after.qasm', to='Surface')

# load circuit(system: IBM)
circuit_path = 'data_surface.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path)

circuit.save('data_surface_after.qasm', to='IBM')