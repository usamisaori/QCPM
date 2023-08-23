import string

from qcpm.operator import Operator
from qcpm.common import countDecorator


class PatternMeta:
    # use Example:
    # operands: "abaa", targets: [1, 2, 1, 1]
    # => that means: books: {'a': 1, 'b': 2, 'c': -1, ...}
    books = { k:-1 for k in string.ascii_lowercase }

    def __init__(self, src, dst):
        """
        src/dst: 
        eg. [ ["rx", [1], "pi/2"], ["cx", [0, 1]], ["x", [1]] ]

        self.src/self.dst:
        eg. {'operaror': 'Xcx', 'operands': 'abaa', 'angles': ["pi/2", '', '']}
        
        """
        self.data = {
            'src': src,
            'dst': dst
        }

        # solved pattern data
        self.src = self._solve_pattern(src)
        self.dst = self._solve_pattern(dst)

        # separatly store each info for convinence
        self.opr = [ self.src['operator'], self.dst['operator'] ]
        self.opd = [ self.src['operands'], self.dst['operands'] ]
        self.angles = [ self.src['angles'], self.dst['angles'] ]
    
    def _solve_pattern(self, target):
        """
        eg. target:
        
        [ 
            ["rx", [1], "pi/2"], 
            ["cx", [0, 1]], 
            ["x", [1]] 
        ],
        
        after _solve_pattern():
        
        {
            "operator": "Xcx",
            "operands": "abaa",
            "angles": ["pi/2", '', '']
        }
        
        """
        operator_pattern = [ Operator.convert_type(operation[0]) for operation in target ]
        # [[1], [0, 1], [1]] => "abaa"
        operands_pattern = [ string.ascii_lowercase[int(operands)] 
            for operation in target for operands in operation[1] ]
 
        # operation: ["cx", [0, 1]] len = 2 => angle = ''
        # operation: ["rx", [1], "pi/2"] len = 3 => angle = operation[-1] = pi/2
        angles_pattern = [  '' if len(operation) == 2 else operation[-1] 
            for operation in target ]
        for i in range(len(angles_pattern)):
            if isinstance(angles_pattern[i], list):
                angles_pattern[i] = ','.join(angles_pattern[i]).replace(' ', '')

        return {
            'operator': ''.join(operator_pattern),
            'operands': ''.join(operands_pattern),
            'angles': angles_pattern
        }
    
    def match(self, operators, positions, *, return_='targets'):
        """ match whether tagets operators(circuit) match this pattern

        Args:
            operators: container of operators, may be Circuit object.
            positions: positions need to check.
            return_: the extra object need to return.
        -------
        Returns:
            bool: True/False: whether mathed.
            extra_object:
                corresponding to return_, will be:

                    - 'targets': targets that contains operands indexes. (default)
                    - 'books': a map about letter to index. eg. 'a' => 1
                    - 'all': dict containes both targets and books. 
        """
        # reset books
        for k in self.books:
            self.books[k] = -1
        
        # Test 1. matched operands
        # 
        # eg. operands: abbc  
        #     targets:  [4, 1, 1, 2] 
        # 
        targets = [ operand for i in range(len(positions))
                            # circuit[index] => operator object,
                            # operator.operands => positions like [1, 4]
                            for operand in operators[positions[i]].operands ]
        
        for i, operand in enumerate(self.opd[0]):
            if self.books[operand] == -1:
                self.books[operand] = targets[i]
            elif self.books[operand] != targets[i]:
                return False, None

        # Test 2. no duplicated operand in books
        #
        # eg. pattern: 'cc', operands: abcb
        #   => cx q[1],q[3]; cx q[1],q[3]; shouldn't match
        #      cause operand a = c = 1 
        operands = set()
        operands_num = 0

        for k in self.books:
            if self.books[k] != -1:
                operands.add(self.books[k])
                operands_num += 1
        
        # there are duplicated operands
        if len(operands) != operands_num:
            return False, None

        # Test 3. matched angles in rotation gates.
        angles = [ operators[positions[i]].angle for i in range(len(positions)) ]

        for i, angle in enumerate(angles):
            if angle != self.angles[0][i]:
                return False, None

        # MATCHED!
        #   => select extra_obj to return
        # remember the returned books should be copy object.
        if return_ == 'targets':
            extra_obj = targets
        elif return_ == 'books':
            extra_obj = self.books.copy()
        elif return_ == 'all':
            extra_obj = {
                'targets': targets,
                'books': self.books.copy()
            }

        return True, extra_obj
    

@countDecorator
class Pattern(PatternMeta):
    def __init__(self, src, dst, index=0):
        super().__init__(src, dst)

        self.index = index
    
    @property
    def delta_cycle(self):
        """ calculate cost saving.

        calculate delta cost-saving after using this pattern

        """
        # eg. opr = ['xcx', 'c']
        # delta: (1 + 2 + 1) - (2)
        return sum(map(Operator.count_qubits, list(self.opr[0]))) - \
            sum(map(Operator.count_qubits, list(self.opr[1])))

    def __repr__(self):
        INDENT = ' ' * 4

        info = 'Pattern: ' + str(self.index + 1) + '\n'

        for i, op in enumerate(self.data['src']):
            info += f'{INDENT}{op[0]}'

            if self.angles[0][i] != '':
                info += f'({self.angles[0][i]})'

            info += ' ' + str(op[1])
            info += '\n'
        
        info += INDENT + "=> \n"
        
        for i, op in enumerate(self.data['dst']):
            info += INDENT
            info += op[0]
            
            if self.angles[1][i] != '':
                info += f'({self.angles[1][i]})'
            
            info += ' ' + str(op[1])
            info += '\n'

        if len(self.data['dst']) == 0:
            info += f'{INDENT}I\n'

        return info