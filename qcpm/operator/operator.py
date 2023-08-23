from qcpm.common import countDecorator
from qcpm.operator.mixin import operatorMixin


class Operator(operatorMixin):
    """ Operator object corresponding to a gate operator.

    Including op_type: like "cx", "h" ...
    and operands which give the corresponding operands' positions in circuit.
    
    - op_type = '_' means this operator should be removed.
    - operands should always be a list. 

    Example:
        input: 'cx', 'q[2],q[4]' 
            => self.type = 'cx', self.operands = [2, 4], self.angle = None
        
        input: 'rz(-pi/2)', 'q[2],q[1]'
            => self.type = 'rz', self.operands = [2, 1], self.angle = "-pi/2"
    """

    ABANDON = '_'
    reject_type = {'qreg', 'creg'}

    @countDecorator
    def __init__(self, op_type, operands, index = 0):
        """
        Args:
            op_type: like "cx", input is the type before converting.
            operands: 
                1. read from QASM: "q[2],q[4]"
                2. deirectly input a list: [2, 4]
        """
        if op_type in self.reject_type:
            raise ValueError(f"value <{op_type}> doesn't mean a operator")

        # self.angle may be changed in self._rotate_filter
        # thus the position of it must be ahead of self.type
        self.angle = ''
        self.type = self._rotate_filter(op_type)
        self.index = index
        
        if isinstance(operands, list):
            # directly input list like: [1, 4]
            self.operands = operands
        else:
            # operands is str like "q[2],q[4]"
            self.operands =  self._solve_operands(operands)    

    def _rotate_filter(self, op_type):
        """ 
        if operator is a rotate Gate, solve to save the angle.

        may change self.angle

        """
        if op_type[0] == 'r':
            # eg. rx(-pi/2) q[1]; 
            #   => op_type = "rx(-pi/2)"
            #   => op_type[3:][:-1] = "-pi/2"
            self.angle = op_type[3:][:-1]

            # op_type[:2] => 'rx'
            return op_type[:2]
        elif op_type[0] == 'u':
            # eg. u2(pi/2, pi/2);
            #   => op_type = "u2(pi/2, pi/2)"
            #   => op_type[3:][:-1] = "pi/2, pi/2"
            #   => replace(" ", "") = "pi/2,pi/2"
            self.angle = op_type[3:][:-1].replace(' ', '')

            return op_type[:2]
        else:
            # and self.angel still None
            return op_type
    
    def _solve_operands(self, operands):
        """ solve operands(str) input.

        Args:
            operands: like "q[2],q[4]"
        -------
        Example:
            "q[2],q[4]" => ["q[2]", "q[4]"]
                        => [2, 4] (return)
        """
        operands = operands.split(',')

        # operand: "q[1]" / "q[10]"
        #   => operand.split('['): ["q[", "10]"]
        #   => ...[1]: "10]"
        #   => ......[:-1]: "10"
        return [int(''.join( operand.split('[')[1][:-1] ) )
                    for operand in operands]

    def change(self, new_type, new_operands=None, new_angle=None):
        """ change info about operator manually

        Args:
            new_type: '_' means to abandon this operator.
                otherwise new_type should be a type before converting, like 'cx'
            new_operands: default: keep the setted operands.
            new_angle: may be str or int/float. 
                => default: keep the setted angle
        """
        if new_type == Operator.ABANDON:
            self.type = new_type

            return
        else:
            self.type = self.convert_type(new_type, True)

        if new_operands != None:
            size = self.count_qubits(self.type)
            # check operands' size
            if len(new_operands) != size:
                raise ValueError(f'Unmatched operands: [{new_operands}] for op:<{self.type}>')

            self.operands = new_operands

        if new_angle != None and new_angle != "":
            self.angle = str(new_angle)
            
            if self.angle[0] == '[':
                self.angle = self.angle[1:-1].replace(' ', '')

        return self

    ######################
    #                    #
    #     Properties     #
    #                    #
    ######################

    @property
    def output(self):
        """ output self as a raw data in QASM.

        1. should ignore ABANDON / empty operands case
        2. should solve case with rotation.

        eg. self.type = 'cx', self.operands = [2, 4]
            => return 'cx q[2],q[4];\n'
        """ 
        if self.type == self.ABANDON or len(self.operands) == 0:
            return ''
        
        # eg. h/rz
        type_output = self.type
        # eg. 'rz', angle: 'pi/2' => 'rz(pi/2)'
        if self.angle != '':
            type_output += f'({self.angle})'
        
        # [1, 2] => "q[1],q[2]"
        operands_output = ','.join([f'q[{opd}]' for opd in self.operands])

        # 'cx', 'q[1],q[2]' => 'cx q[1],q[2];\n' remember the ';\n' in the end.
        return f'{self.__class__.convert_type(type_output, True)} {operands_output};\n'

    ##########################
    #                        #
    #     Dunder Methods     #
    #                        #
    ##########################

    def __repr__(self):
        # eg. "No. 1, cx [1, 2]"
        return "No: {}, {} {}".format(self.index, self.type, self.operands)