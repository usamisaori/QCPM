from itertools import zip_longest
from copy import copy, deepcopy

from qcpm.operator import Operator
class Candidate:
    """ Candidate object that contains mapped gates' positions etc.

    called in Mapper.execute( => find )

    """
    def __init__(self, pos, pattern):
        """
        Args:
            pos: eg. [1, 4]
            pattern: corresponding pattern like:
                pattern.src/dst => {'operator': 'xx', 'operands': 'aa'}
        """
        self.pos = pos
        self.size = len(pos)
        self.delta_size = len(pattern.src['operator']) - len(pattern.dst['operator'])
        
        self.begin = pos[0]
        self.end = pos[-1]

        # Pattern.src / Pattern.dst => {'operator': 'xx', 'operands': 'aa'}
        # 
        # Pattern.opr = ['xcx', 'c']
        # Pattern.opd = ['aaba', 'ab']
        self.pattern = pattern # Pattern object

    def __repr__(self):
        dst = self.pattern.opr[1]
        if dst == '':
            dst = 'I'
        
        return f"Pos: {self.pos} {self.pattern.opr[0]} => {dst}"

    def __and__(self, other):
        """ check whether self(Candidate) conflicts with other

        Args:
            other: may be => None,  
                Candidate,  [Candidate, ...],
                [1, 2, 3, ...], set{1, 2, 3}
        -------
        Example:
            Candidate1 & Candidate2 == True
                => conflict existing.
        """
        if other is None:
            return False

        try:
            # other is Candidate.
            return len(set(self.pos) & set(other.pos)) != 0
        except:
            if isinstance(other, list) and len(other) != 0:
                # if other is list of Candidate
                if isinstance(other[0], Candidate):
                    for candidate in other:
                        if self & candidate:
                            return True
                    # no conflict between self and [Candidate, ...]
                    return False
                
            # int positions list / set
            return len(set(self.pos) & set(other)) != 0

    def delta(self, metric, circuit=None):
        """ calculate delta value of applying this candidate.

        Args:
            metric: cycle / depth using to calculate value of this candidate
            circuit: calculate delta_depth may need to use circuit info. 
                => default None, won't be used in calculate delta_cycle
        """
        if metric == 'cycle':
            return self.delta_cycle
        elif metric == 'depth':
            return self.delta_depth(circuit)

    @property
    def delta_cycle(self):
        """ calculate cost saving.

        calculate delta cost-saving after using this candidate

        """
        if '_cycle' not in self.__dict__:
            self._cycle = self.pattern.delta_cycle

        return self._cycle
    
    def delta_depth(self, circuit):
        """ calculate the delta depth after apply this candidate in a sub circuit.

        Args:
            circuit: a Circuit object corresponding to the total circuit
                => will cut a sub-circuit to calculate delta_depth value.
        """
        if '_depth' in self.__dict__:
            return self._depth

        # sub size before and after circuit
        SUB_SIZE = 20

        # Step 1. cut sub-circuit
        sub_circuit = copy(circuit)
        sub_begin = self.begin - SUB_SIZE if self.begin - SUB_SIZE>= 0 else 0
        sub_end = self.end + SUB_SIZE if self.end + SUB_SIZE < len(circuit) else len(circuit) - 1
        sub_circuit.operators = deepcopy(circuit[sub_begin:sub_end + 1])

        # Step 2. adjust the candidate's position according to the new beginning of subcircuit
        self.begin -= sub_begin
        self.end -= sub_begin
        self.pos = [p - sub_begin for p in self.pos]

        # Step 3. apply this candidate on subcircuit to calculate delta of depth
        depth_before = sub_circuit.depth
        self.apply(sub_circuit, silence=True)
        depth_after = sub_circuit.depth

        # Step 4. ! recover the origin positions
        self.begin += sub_begin
        self.end += sub_begin
        self.pos = [p + sub_begin for p in self.pos]

        # Step 5. calculate self delta_depth and memoize it.
        self._depth = depth_after - depth_before + 1

        return self._depth

    def apply(self, circuit, silence=False):
        """ apply this candidated-mapping in the Circuit.

        called by Mapper.execute => Plans.apply

        Args:
            circuit: Circuit object
            silence: [True] that ignore the apply info output. default [False].
        """
        # example 1:
        # --------------------
        # self.pos: eg. [1, 6]
        # self.pattern.src: eg. {'operator': 'cc', 'operands': 'abab', 'angles': ['', '']}
        # self.pattern.dst: eg. {'operator': '', 'operands': '', 'angles': ['', '']}
        # 
        # example 2:
        # --------------------
        # self.pos: eg. [1, 4]
        # self.pattern.src: eg. {'operator': 'cc', 'operands': 'abbc', 'angles': ['', '']}
        # self.pattern.dst: eg. {'operator': 'c', 'operands': 'ac', 'angles': ['', '']}
        #
        _, books = self.pattern.match(circuit, self.pos, return_='books')

        cur = 0
        ops_from, ops_to = self.pattern.opr
        operands_to = self.pattern.dst['operands']
        angles_to = self.pattern.angles[1]

        # Output apply info.
        silence or print('Apply: ', self.__repr__())

        for i, (op_from, op_to, angle_to) in enumerate(zip_longest(ops_from, ops_to, angles_to)):
            # eg. h => 1, c => 2 ...
            size = Operator.count_qubits(op_to)
            # eg. 'ab' => [1, 4]
            operands = [ books[operand] for 
                operand in operands_to[cur: cur + size] ]

            if op_to == None:
                op_to = Operator.ABANDON
            
            # apply => change this operator in circuit.
            circuit[self.pos[i]].change(
                op_to, # new operator
                operands,
                angle_to
            )

            cur += size