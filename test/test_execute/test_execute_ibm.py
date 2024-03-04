import sys
sys.path.append('../../')

from qcpm import Circuit, Mapper


originOutput = sys.stdout
file = open('execute_ibm.txt', 'w')
sys.stdout = file

print('Load circuit data and execute mapping: \n')

mapper = Mapper()

# load circuit(system: IBM)
circuit_path = '../data/data_ibm.qasm'
print(f'Try execute mapping on <{circuit_path}>: ')
circuit = Circuit(circuit_path)
mapper.execute(circuit)

circuit.save('data_ibm_after.qasm')
sys.stdout = originOutput