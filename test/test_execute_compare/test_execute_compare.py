import sys
sys.path.append('../../')

from qcpm import Circuit, Mapper


originOutput = sys.stdout
print('Compare different strategy using to execute mapping: \n')
mapper = Mapper()


file = open('execute_normal_strategy.txt', 'w')
sys.stdout = file

# load circuit(system: IBM)
circuit_path = '../data/data_ibm.qasm'
print(f'Try execute mapping on <{circuit_path}>: ')

# call optimize - mapping .. for two rounds.
# remember that when init Cirucit do the first optimization.

# normal strategy:
circuit = Circuit(circuit_path)
mapper.execute(circuit, silence=True)
circuit.optimize()
mapper.execute(circuit, silence=True)
print(circuit.info)


file = open('execute_mcm_strategy.txt', 'w')
sys.stdout = file

# MCM based mapping:
circuit = Circuit(circuit_path)
mapper.execute(circuit, strategy='MCM', silence=True)
circuit.optimize()
mapper.execute(circuit, strategy='MCM', silence=True)
print(circuit.info)

sys.stdout = originOutput