from turtle import circle
from qcpm import QCPatternMapper



"""
    params:
        - log: eg 'log.txt', path of output log file. (for single file) default ''
        - logs: log files' output dir default './log/'
"""
QCPM = QCPatternMapper()

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


# solving files in batch mode(dir to dir):
# input_dir / output_dir
config = {
    # 'logs': './logs/', # for files
    'stat': './', # csv path
    # 'strategy': 'MCM',
    'system': ["Surface", "IBM"],
    # 'system': ["IBM", "U"], # ['IBM', 'Surface', 'U']
    # 'system': ["U", "Surface"],
    # 'system': ["Surface", "U"],
    # 'depth_size': 'medium', # default all
    'metric': 'cycle' # cycle or depth
}
# QCPM.execute('../data/stat-test/', '../data/stat-output/', **config)
# QCPM.execute('../data/simulation-test/', '../data/simulation-output/', **config)
# QCPM.execute('../data/shor', '../shor_result_U', **config)
# QCPM.execute('../shor_result_U', '../shor_result_IBM', **config)
# QCPM.execute('../shor_result_U', '../shor_result_surface', **config)
# QCPM.execute('../shor_result_surface', '../shor_result_U', **config)
QCPM.execute('../data/single_cz', '../cz_result', **config)