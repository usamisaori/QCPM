import sys
sys.path.append('../../')

from qcpm import Circuit, Mapper

print('Load circuit data and execute mapping(MCM): \n')

mapper = Mapper()

# load circuit(system: IBM)
circuit_path = 'data_ibm.qasm'
print(f'Try execute mapping on <{circuit_path}>: ')
circuit = Circuit(circuit_path)
mapper.execute(circuit, strategy='MCM')

circuit.save('data_ibm_after.qasm')


print('-' * 50 + '\n')


# load circuit(system: Surface)
circuit_path = 'data_surface.qasm'
print(f'Try execute mapping on <{circuit_path}>: ')
circuit = Circuit(circuit_path, system='Surface')
mapper.execute(circuit, strategy='MCM')

circuit.save('data_surface_after.qasm')