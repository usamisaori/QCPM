import json
import pkgutil
from itertools import zip_longest
from copy import deepcopy

from qcpm.operator import Operator
from qcpm.pattern.pattern import Pattern


class Expander:
    """ Expander that expand single op to concreate operators, like: swap => cx cx cx

    """
    def __init__(self, system='IBM'):
        self.patterns = {} # contains Pattern object.
        self._init_patterns()

        self.system = system

    def _init_patterns(self):
        """ load pattern file and initiate

        load pattern json file and init self.patterns
        will load all system's pattern info in advance.

        """
        systems = ['IBM', 'Surface', 'U']
        self.patterns = {} # reset to empty

        for system in systems:
            data = pkgutil.get_data(__package__, f'/rules/{system}/expansion.json')
            patterns_data = json.loads(data.decode())

            self.patterns[system] = []

            # pattern: 
            # {
            #     "src": [ ["swap", [0, 1]] ],
            #     "dst": [ ["cx", [0, 1]],["cx", [1, 0]],["cx", [0, 1]] ]
            # }
            for pattern in patterns_data:
                # Pattern(src, dst)
                self.patterns[system].append( Pattern(**pattern) )

    def check(self, operator):
        """ Check whether a operator need to expand

        Returns:
            ok: True if this operator do need to expand.
            pattern: a expansion pattern corresponding to this operator, or None
        """

        for pattern in self.patterns[self.system]:
            # pattern.data['src']: [ ["swap", [0, 1]] ]
            #   => [0][0]: 'swap'
            if operator.type == pattern.data['src'][0][0]:
                return True, pattern
            
        return False, None 

    def expand(self, operator, pattern):
        """ expand operator according to expansion pattern

        will generate operators

        """
        _, books = pattern.match([operator], [0], return_='books')

        _, ops_to = pattern.opr
        operands_to = pattern.dst['operands']
        angles_to = pattern.angles[1]

        cur = 0
        for (op_to, angle_to) in zip_longest(ops_to, angles_to):
            # eg. h => 1, c => 2 ...
            size = Operator.count_qubits(op_to)
            # eg. 'ab' => [1, 4]
            operands = [ books[operand] for 
                operand in operands_to[cur: cur + size] ]
            
            new_operator = deepcopy(operator)
            new_operator.change(
                op_to, # new operator
                operands,
                angle_to
            )
            yield new_operator

            cur += size

    def __call__(self, operators):
        for operator in operators:
            ok, pattern = self.check(operator)
            
            if ok:
                yield from self.expand(operator, pattern)
            else:
                yield operator