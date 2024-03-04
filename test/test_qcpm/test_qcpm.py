import sys
sys.path.append('../../')

from qcpm import QCPatternMapper


"""
    params:
        - log: eg 'log.txt', path of output log file. (for single file) default ''
        - logs: log files' output dir default './log/'
"""
QCPM = QCPatternMapper(log='./output_qcpm.txt')

# solving single file:
"""
    params:
        - optimize: Whether to optimize, default: True
        - system: 
                - if in/out is the same system: "IBM" / "Surface"
                - else: array of in/out systems like: ["IBM", "Surface"]
        - metric: "cycle" / "depth" used to calculate value of candidate.
        - stratrgy: strategy use to generate mapping plan, "MCM"/"random"
            default(None) greedy search.
"""
# QCPM.execute(circuit_path, './circuit_after', 
#     strategy='random', system='IBM', metric='depth')

QCPM.execute('../data/data_ibm.qasm', './data_ibm_after', metric='cycle')
