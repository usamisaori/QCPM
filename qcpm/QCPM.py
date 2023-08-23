import os
import sys
from contextlib import contextmanager

from qcpm.pattern import Mapper
from qcpm.circuit import Circuit
from qcpm.common import Timer
from qcpm.statistics import StatReporter
from qcpm.config import QCPMConfig


stdout = sys.stdout

@contextmanager
def logging(log_path, mode='a'):
    """ logging context management

    enter: redirect stdout to log_file(according to log_path)
        if log_paht is '' no redirect
    leave: recover the sys.stdout to origin stdout

    """
    if log_path != '':
        # redirect to log file
        log_file = open(log_path, mode)
        sys.stdout = log_file
    
    try:
        yield
    finally:
        if log_path != '':
            log_file.close()
        
        sys.stdout = stdout

class DepthSizeError(ValueError):
    """ when solving qasm file's depth size(small/medium/large)
        dismatch the expected depth size, this error will occur.
    
    """
    pass


############################
#                          #
#     Class Definition     #
#                          #
############################

class QCPatternMapper:
    """ Quantum circuit pattern mapper Class.

    Example:
        QCPM = QCPatternMapper()

        # 1. single file to file
        QCPM.execute(circuit_path, './circuit_after')

        # 2. dir to dir (batch work)
        QCPM.execute('./data/', './output/', strategy='MCM')
    
    """

    def __init__(self, **kwargs):
        """ 
        Args:
            pattern_path: json file about patterns.
            log: log file to redirect. default '' means to log in stdout.
        """
        self.log = kwargs.get('log', '') # log file path
        self.logs = kwargs.get('logs', './log/') # log files' output dir
        self.reporter = None

        with logging(self.log, 'w'):
            self.mapper = Mapper()

    def execute(self, input_path, output_path='', **kwargs):
        """ apply mapper on target circuit.

        If input path is dir => call self._executeDir

        Args:
            input_path: qasm file's path or may be qasm files' dir path.
            output_path: default='' means no output.
        """
        # init config object
        self.config = QCPMConfig(kwargs)

        self._execute(input_path, output_path)

        # destroy config object
        self.config = None

    def _execute(self, input_path, output_path=''):
        """ apply mapper on target circuit.

        If input path is dir => call self._executeDir

        Args:
            input_path: qasm file's path or may be qasm files' dir path.
            output_path: default='' means no output.
        """
        # if input_path is a folder path => batch work model
        if os.path.isdir(input_path):
            self._executeDir(input_path, output_path)
            return 

        if isinstance(self.config.system, list):
            # eg. system = ["IBM", "Surface"]
            system_input, system_output = self.config.system
        else:
            # eg. system = 'Surface'
            system_input = system_output = self.config.system
        
        timer = Timer()
        timer.silence = True

        with logging(self.log):
            with timer:
                # execute turns limit.
                # in each turn: 
                # ---------------
                # 1. optimization: reduction -> commutation ...(×n)... -> reduction
                # 2. pattern mapping: mapper.execute(circuit)
                # 
                LIMIT = 5

                turn = 1
                # first turn should initial circuit(default call optimization.)
                circuit = Circuit(input_path, system=system_input, optimize=self.config.optimize)

                # after loading circuir, check the depth size
                circuit_depth_size = circuit.origin.depth_size
                if self.config.depth_size != 'all' and circuit_depth_size != self.config.depth_size:
                    raise DepthSizeError(circuit_depth_size)
                
                changed = self.mapper.execute(circuit, 
                    system=system_input, strategy=self.config.strategy, metric=self.config.metric)

                while changed and turn < LIMIT:
                    self.config.optimize and circuit.optimize()
                    
                    changed = self.mapper.execute(circuit,
                        system=system_input, strategy=self.config.strategy, metric=self.config.metric)

                    turn += 1

                if output_path != '':
                    # save qasm file (after mapping)
                    circuit.save(output_path, system=system_output)
                
                self.mapper.result()
            # end of timer
        # end of logger
        
        if self.reporter != None:
            # statistic reporter: (filename, circuitInfos, time)
            self.reporter.add(input_path, [circuit.origin, circuit.info], timer.duration)

        print(circuit)

    def _executeDir(self, input_dir, output_dir):
        """ execute when call batch work form dir to dir.

        Iterately call [self.execute] to execute.

        Args:
            input_dir/output_dir: file folder path. (from => to)
            [! Other args should be corresponding to self.execute] => **kwargs
        
        """
        self.reporter = StatReporter(self.config.stat_path, 
            metric=self.config.metric, folder=input_dir, config=self.config)

        for i, file in enumerate(os.listdir(input_dir)):
            # eg. 'example.qasm'
            # filename => 'example'
            filename = os.path.splitext(file)[0]
            # output_name => 'example_output'
            output_name = f'{filename}_output'
            
            print(f'solving {i + 1}-th file <{input_dir}{filename}.qasm>...', sep='')

            # default log file will be ./log/example_log.txt
            self.log = f'{self.logs}{filename}_log.txt'
            
            try:
                # call self.execute to solve single file.
                self._execute(
                    os.path.join(input_dir, f'{filename}.qasm'),
                    os.path.join(output_dir, f'{output_name}.qasm'),
                )

                print(f'-- finished! output: <{output_dir}{output_name}>.')
                print(f'---- log file in [{self.log}].\n')

            except DepthSizeError as e:
                print(f'-- depth size: [{e}] IGNORE it.\n')
