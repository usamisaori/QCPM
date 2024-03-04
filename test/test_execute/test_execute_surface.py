import sys
sys.path.append('../../')

from qcpm import Circuit, Mapper


originOutput = sys.stdout
file = open('execute_surface.txt', 'w')
sys.stdout = file

print('Load circuit data and execute mapping: \n')

mapper = Mapper()

# load circuit(system: Surface)
circuit_path = '../data/data_surface.qasm'
print(f'Try execute mapping on <{circuit_path}>: ')
circuit = Circuit(circuit_path, system='Surface')
mapper.execute(circuit)

circuit.save('data_surface_after.qasm')
sys.stdout = originOutput
