import sys
sys.path.append('../../')

from qcpm import Circuit, Mapper

print('Compare different strategy using to execute mapping: \n')

mapper = Mapper()

# load circuit(system: IBM)
circuit_path = 'data_ibm.qasm'
print(f'Try execute mapping on <{circuit_path}>: ')

# call optimize - mapping .. for two rounds.
# remember that when init Cirucit do the first optimization.

# normal strategy:
circuit = Circuit(circuit_path)
mapper.execute(circuit, silence=True)
circuit.optimize()
mapper.execute(circuit, silence=True)
print(circuit.info)

print('-' * 50 + '\n')

# MCM based mapping:
circuit = Circuit(circuit_path)
mapper.execute(circuit, strategy='MCM', silence=True)
circuit.optimize()
mapper.execute(circuit, strategy='MCM', silence=True)
print(circuit.info)