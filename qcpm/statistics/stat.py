import time
from os.path import dirname, basename

from qcpm.statistics.create import create
from qcpm.statistics.addrow import addRow


class StatReporter:
    def __init__(self, path, **kwargs):
        if path == None:
            self._state = False
            return
        else:
            self._state = True

        # csv file's name:
        # eg. 2022-03-07_20.50.50

        name = self.initCSVName(**kwargs)
        self.path = f'{path}{name}.csv'
        self.metric = kwargs.get('metric', 'cycle')

        create(self.path, self.metric)

    def initCSVName(self, *, metric, folder, config):
        # %m%d%H%M_dirname_[optimize]_[strategy]_[systems]_[metric]
        timestamp = time.strftime('%m%d%H%M', time.localtime(time.time()))

        name = basename(dirname(folder))

        optimize = config.optimize
        strategy = config.strategy
        metric = config.metric

        if isinstance(config.system, list):
            # eg. system = ["IBM", "Surface"]
            system = '_to_'.join(config.system)
        else:
            # eg. system = 'Surface'
            system = config.system

        return f'{timestamp}_{name}_{optimize}_{strategy}_{system}_{metric}'

    def add(self, filename, circuitInfos, time):
        if self._state == False:
            # no need to report: eg. solving single file.
            return

        addRow(self.path, filename, circuitInfos, self.metric, time)