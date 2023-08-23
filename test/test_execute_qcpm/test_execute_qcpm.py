import sys
sys.path.append('../../')

from qcpm import QCPatternMapper

print('Execute mapping through QCPatternMapper: \n')

QCPM = QCPatternMapper()

# circuit_path = 'data_ibm.qasm'
# solve single qasm file
# QCPM.execute(circuit_path, './data_ibm_after.qasm', silence=True)
# QCPM.execute(circuit_path, './data_ibm_after_mcm.qasm', strategy='MCM', silence=True)

circuit_path = 'data_surface.qasm'
# solve single qasm file
QCPM.execute(circuit_path, './data_surface_after.qasm', 
    silence=False, system='Surface')
QCPM.execute(circuit_path, './data_surface_after_mcm.qasm', 
    strategy='MCM', silence=False, system='Surface')