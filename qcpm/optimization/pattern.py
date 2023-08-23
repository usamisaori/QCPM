from collections import deque

from qcpm.pattern import PatternMeta
from qcpm.operator import Operator


##########################
#                        #
#     Tool functions     #
#                        #
##########################

def gatherTypes(ops):
    """
    Args:
        ops: list of Operator object like:
            => [Operator('h'), Operator('cx'),...]
    -------
    Returns: 
        str about op_type of each Operator, like:
            => 'hc...'
    """
    return ''.join(Operator.convert_type(op.type) for op in ops)

def matchTypes(opstr, pattern):
    """
    Args:
        opstr: like 'cchsh', str of op_types
        pattern: like 'hsh', str of a pattern
    -------
    Returns: 
        matched => True, else => False
    """
    size = len(pattern)

    if len(opstr) < size:
        return False
    else:
        # opstr ends with pattern ?
        return opstr.endswith(pattern)


############################
#                          #
#     Class definition     #
#                          #
############################

class ReductionPattern(PatternMeta):
    def __init__(self, src, dst):
        # self.src/dst = 
        # eg. {'operaror': 'ccc', 'operands': 'abbcab', 'angles': ['', '', '']}
        super().__init__(src, dst)

        self.size = len(self.src['operator'])

    def _matchTypes(self, ops):
        return matchTypes(
            gatherTypes(ops), # opstr like 'xxcxccc'
            self.src['operator'] # like 'ccc'
        )

    def map(self, ops):
        """ Map reduction.

        Example:
            call: pattern.map(ops)
        """
        # Step 1. test operator matching
        if not self._matchTypes(ops):
            return False

        # Step 2. test operands matching
        # detail matching is implemented in qcpm.pattern.pattern
        # -----------------------------
        ok, books = self.match(
            ops, 
            # eg. ops = 'xxhccc' => len = 6
            #     pattern: 'ccc' => self.size = 3
            # thus positions = [range(6 - 3, 6)] => [3, 4, 5]
            list( range( len(ops) - self.size, len(ops) ) ), 
            return_='books'
        )
        if not ok:
            return False
        # else: # matched ReductionPattern:
        #   apply reduction:

        # Step 3. pop old ops
        # ------------------------------
        # hscSh => Scs
        # operands: aabaaa => abaa
        # books: books[a] = 0, books[b] = 1
        for i in range(self.size):
            ops.pop()

        # Step 4. append new operator
        # ------------------------------
        cur = 0
        # eg. dst_operator = 'xY', dst_operands = 'aa', dst_angles = [None, "-pi/2"]
        dst_operator, dst_operands = self.dst['operator'], self.dst['operands']
        dst_angles = self.dst['angles']

        for _, operator in enumerate(dst_operator):
            # eg. operator = 'c' => operands_size = 2
            operands_size = Operator.count_qubits(operator)
            # if books = {'a': 1, 'b': 4, ...}
            # then operands "ab"  => [1, 4]
            operands = [ books[dst_operands[cur + k]] for k in range(operands_size) ]

           # Operator.op_type should be original type just like in QASM, eg. cx
            # Operator.convert_type(operator, True):
            #   => 'Y' => 'ry'
            op_type = Operator.convert_type(operator, True)
            # if is rotation like rz => rz(pi/2) while pi/2 info is from dst_angles
            if Operator.is_rotation(op_type):
                op_type = f'{op_type}({dst_angles[i]})'
            
            ops.append( Operator(op_type, operands) )

            cur += operands_size


class CommutationPattern(ReductionPattern):
    def __init__(self, src, dst):
        # self.src/dst = eg. {'operaror': 'ccc', 'operands': 'abbcab'}
        super().__init__(src, dst)

    def map(self, ops):
        """ Map commutation.

        Example:
            call: pattern.map(ops)
        """
        # Step 1. test operator matching
        if not self._matchTypes(ops):
            return False

        # Step 2. test operands matching
        # detail matching is implemented in qcpm.pattern.pattern
        # -----------------------------
        ok, _ = self.match(
            ops, 
            list( range( len(ops) - self.size, len(ops) ) )
        )
        if not ok:
            return False

        # Step 3. commutate
        # -----------------------------
        # example: "abcd" => "dcba"
        # 
        temp = deque()
        for i in range(self.size):
            temp.append(ops.pop())

        for i in range(self.size):
            ops.append(temp.popleft())