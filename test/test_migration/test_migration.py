import sys
sys.path.append('../../')

from qcpm import Circuit


print('Migration test \n')

# load circuit(system: IBM)
circuit_path = '../data/data_ibm.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path) # default system='IBM'

circuit.save('data_ibm_after.qasm', system='Surface')


# load circuit(system: Surface)
circuit_path = '../data/data_surface.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path)

circuit.save('data_surface_after.qasm', system='IBM')


# load circuit(system: IBM)
circuit_path = '../data/data_ibm_for_u.qasm'
print(f'Try load <{circuit_path}>: ')
circuit = Circuit(circuit_path)

circuit.save('data_u_after.qasm', system='U')
