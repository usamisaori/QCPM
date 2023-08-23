
class QCPMConfig:
    def __init__(self, kwargs):
        self.optimize = kwargs.get('optimize', True)
        self.strategy = kwargs.get('strategy', None)
        self.metric = kwargs.get('metric', 'cycle')

        self.depth_size = kwargs.get('depth_size', 'all') # small/medium/large
        self.system = kwargs.get('system', 'IBM')

        self.stat_path = kwargs.get('stat', None)
        