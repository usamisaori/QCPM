import pkgutil
import json

from qcpm.optimization.pattern import ReductionPattern, CommutationPattern


class Invoker:
    """ Callable Object that map patterns on Operators

    detail patterns info will be decided by subclass.

    """
    def __init__(self, name, system='IBM'):
        # patterns data => self.rules
        data = pkgutil.get_data(__package__, f'/rules/{system}/{name}.json')
        self.rules = json.loads(data.decode())

        self.patterns = [] # should set by subclass

        # the max/min size of operator need to match in all patterns
        self.min_size = len(min(self.rules, key=lambda rule:len(rule['src']))['src'])
        self.max_size = len(max(self.rules, key=lambda rule:len(rule['src']))['src'])

    def __call__(self, ops):
        """
        thus Invoker is callable.
        the specific mapping operation will be decided by pattern's type.
        eg. ReductionPattern or CommutationPattern etc.
        
        """
        if len(ops) < self.min_size:
            return

        for pattern in self.patterns:
            pattern.map(ops)


class Reducer(Invoker):
    def __init__(self, name, system='IBM'):
        super().__init__(name, system)

        self.patterns = [ ReductionPattern(**rule) for rule in self.rules ]


class Commutator(Invoker):
    def __init__(self, system='IBM'):
        super().__init__('commutation', system)

        self.patterns = [ CommutationPattern(**rule) for rule in self.rules ]