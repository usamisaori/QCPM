import os

from qcpm.circuit.info import CircuitInfo
from qcpm.preprocess import preprocess
from qcpm.expander import Expander
from qcpm.optimization import optimizer, reduction
from qcpm.operator import Operator
from qcpm.migration import migrate
from qcpm.common import timerDecorator


class Circuit:
    """ Circuit object creating by QASM file.

    Default using optimization when loading.
    when load origin circuit without optimization: 
        => circuit = Circuit(path, optimize=Fasle)

    Example:
        data: cx q[4],q[1]; t q[4]; t q[2]; h q[0]; ...
            => operators: [Operator, Operator ...] (eg. Operator: cx [4,1])
            => draft: ctth...(cx => c)
    """
    @timerDecorator(description='Init Circuit')
    def __init__(self, path, *, optimize=True, system='IBM'):
        self.system = system # may be 'IBM' / 'Surface' / 'U'

        self.operators = []
        self.draft = '' # solved circuit's gates string

        # CircutiInfo objects
        ## circuit info of current circuit.
        ## store the CirucitInfo and set by calling: circuti.info
        ## may be reseted during optimize() / update()
        self._info = None
        ## circuit info of origin circuit, setted during _load_circuit
        self.origin = None

        self._load_circuit(path, optimize)

    def _load_circuit(self, path, optimize):
        """ init Circuit according to QASM file.

        load data from a QASM file. 
        Init self.operators and self.draft.
        also keep the CircuitInfo of origin circuit in self.origin

        Args:
            path: path of QASM file.
            optimize: whether use optimize. default: True(using)
        """
        operators = []
        op_types = []

        # Step 1. preprocess
        ops = preprocess(path) # iterator
        ## 1.1 Keep the header info of qasm
        ## eg. ['OPENQASM 2.0;\n', 'include "qelib1.inc";\n', 'qreg q[4];\n', ...]
        self.header = next(ops)

        ## 1.2 init origin circuitInfo object
        for operator in ops:
            operators.append(operator)
            # cx = convert_type() => c
            optimize or op_types.append( Operator.convert_type(operator.type) )
        
        # keep the origin ciruit's info object
        self.origin = CircuitInfo(operators, self.system)


        # Step 2. expand gates
        expanded_operators = []
        op_types = []
        expander = Expander(self.system)

        for operator in expander(operators):
            expanded_operators.append(operator)
            # cx = convert_type() => c
            op_types.append( Operator.convert_type(operator.type) )
        
        operators = expanded_operators


        # Step 3. system migrate
        # if system type is not IBM => migrate right now

        if self.system != 'IBM':
            # # maigration self.system to [IBM]
            # # eg. 'Surface' => 'IBM'
            # # 
            # op_types = []
            # migrated_operators = []

            # for operator in migrate(operators, self.system, 'IBM'):
            #     # cx = convert_type() => c
            #     op_types.append( Operator.convert_type(operator.type) )
            #     migrated_operators.append(operator)

            # operators = migrated_operators
            # self.system = 'IBM'
            pass


        if optimize:
            # optimize will save the self.operators and self.draft
            self.optimize(operators)
        else:
            # keep the gates string of origin input circuit.
            self.operators = operators
            self.draft = ''.join(op_types)

    def _optimize(self, operators, *, optimizer=optimizer):
        """ optimization during each turn

        using [optimizer] in ./optimization
            => Reduction -> Commutation
        
        will keep the self.draft but return optimized operators to optimize() 
        whether keep the final self.operators thus is decided by optimize()

        Args:
            operators: iteratable Operators object.
            optimizer: optimizer using to optimize operators.
                => eg. qcpm.optimization.optimizer / qcpm.optimization.reduction
                => if None, just read in without optimization.
        -------
        Returns:
            changed[bool]:
                - True => will still call _optimize unless the turns of 
                    optimization is over the LIMIT.
                - False => Stop useless optimization. 
        """
        temp_operators = []
        op_types = []

        # get iterator of operators after optimization
        if optimizer == None:
            targets = operators
        else:
            targets = optimizer(operators, self.system)

        # solve each operator
        for operator in targets:
            temp_operators.append(operator)
            # cx = convert_type() => c
            op_types.append( Operator.convert_type(operator.type) )
        
        draft = ''.join(op_types)
        changed = draft != self.draft

        self.draft = draft

        return changed, temp_operators
    
    def optimize(self, operators=None, *, iteration=3):
        """ Optimize the loaded circuit by each Operator until no change occurs

        using _optimize() while no change occurs.
        will keep the optimized operators in [self.operators]
        and also keep the [self.draft] through subroutine: _optimize()

        Args:
            operators: iteratable Operators object.
                => if operators is None, optimize circuit(self) itself.
            iteration: iteration turns that optimization. default=3
        """
        if operators == None:
            operators = self

        count = 0
        while count < iteration:
            # optimize: reduction -> commutation
            changed, operators = self._optimize(operators)

            if not changed:
                # after reduction -> commutation -> ... -> reduction -> commutation
                # at last: apply reduction.
                _, operators = self._optimize(operators, optimizer=reduction)
                break
            
            count += 1
        
        self.operators = operators
        self._info = None # reset circuitInfo

    def update(self):
        """ using self.operators re-calculate self.draft

        using after mapping(execute) application.
        abandon the operator which has type: Operator.ABANDON

        """
        self.operators = list(
            filter(
                lambda op: op.type != Operator.ABANDON, 
                self.operators
            )
        ) # abandon operators which has type: Operator.ABANDON(like '_').

        op_types = []

        for operator in self.operators:
            op_types.append( Operator.convert_type(operator.type) )

        # update circuit's draft representation.
        self.draft = ''.join(op_types)
        self._info = None # reset circuitInfo
    
    def save(self, path, system=None):
        """ save code of this circuit to path

        save self.QASM to file(given by path)

        Args:
            path: like ./circuit (default extension: .qasm)
            system: target system type, default None. maybe 'IBM'/'Surface'...
        """
        if system != None and system != self.system:
            # maigration self.system to [to]
            # eg. 'IBM' => 'Surface'
            # 
            op_types = []
            migrated_operators = []

            for operator in migrate(self, self.system, system):
                # cx = convert_type() => c
                op_types.append( Operator.convert_type(operator.type) )
                migrated_operators.append(operator)

            # update circuit's draft representation.
            self.draft = ''.join(op_types)
            self.operators = migrated_operators
            self.system = system

        # default to save as qasm file.
        path = path + '.qasm' if os.path.splitext(path)[-1] == '' else path

        with open(path, 'w') as file:
            file.write(self.QASM)

    ######################
    #                    #
    #     Properties     #
    #                    #
    ######################

    @property
    def cycle(self):
        return sum(map(Operator.count_qubits, [op.type for op in self.operators]))

    @property
    def depth(self):
        return CircuitInfo.compute_depth(self)

    @property
    def info(self):
        """ return circuitInfo of this circuit.

        the CircuitInfo object is stored in self._info which would not initial
        before using it. (may not exist or being None.)
        
        optimize() and update()(after mapper.execute()) may reset self._info.

        return:
            self._info: circuitInfo object. if there's no change occured in circuit
                there's thus no need to re-call CircuitInfo() but return stored object. 
        """
        if '_info' not in self.__dict__ or self._info == None:
            self._info = CircuitInfo(self, self.system)
        
        return self._info

    @property
    def QASM(self):
        """ return QASM code representation of this circuit.
        
        """
        # remember header: eg. ['OPENQASM 2.0;\n', ...]
        code = ''.join(self.header)

        for op in self:
            code += op.output

        return code

    ##########################
    #                        #
    #     Dunder Methods     #
    #                        #
    ##########################
        
    def __len__(self):
        # len(circuit) <=> len(circuit.draft)
        return len(self.draft)
    
    def __getitem__(self, index):
        # thus circuit[i] <=> circuit.operators[i]
        return self.operators[index]

    def __repr__(self):
        # if Circuit: cx h cx sdg ...
        # => draft: chcS...
        # => this: cx-h-cx-sdg-...
        return '-'.join(map(lambda op: op.type, self))