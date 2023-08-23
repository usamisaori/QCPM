class operatorMixin:

    op_type_map = {
        'id': 'I',
        # two qubits gates
        'swap': 'w',
        ## control gates
        'cx': 'c',
        'cz': 'e',

        # phase and rotation:
        'tdg': 'T',
        'sdg': 'S',
        # rotation gates
        'rx': 'X',
        'ry': 'Y',
        'rz': 'Z',

        'u1': '1',
        'u2': '2',
        'u3': '3',

        # three qubtis gates
        'tof': 'F',
        'ccx': 'F',
        'ccz': 'C'
    }
    # {'I': 'id' ...}
    op_type_map_reversed = {v:k for (k,v) in op_type_map.items()}

    rotation_gates = ['rx', 'ry', 'rz', 'u1', 'u2', 'u3']

    multi_qubits_gate = {
        'cx': 2,
        'cz': 2,
        'tof': 3,
        'ccx': 3,
        'ccz': 3,
        'swap': 2,
    }

    @classmethod
    def convert_type(cls, op_type, reverse=False):
        """
        Example: 
            reverse=False: cx => c, id => I...
            reverse=True: c => cx, I => id...
        """
        try:
            if not reverse:
                return cls.op_type_map[op_type]
            else:
                return cls.op_type_map_reversed[op_type]
        except KeyError:
            # op_type is not in op_type_map/op_type_map_reversed
            return op_type

    @classmethod
    def count_qubits(cls, op):
        """ count the operands size of operator
        
        """
        # get original op_type
        if op not in cls.op_type_map:
            op = cls.convert_type(op, True)

        # default qubits size: 1
        return cls.multi_qubits_gate.get(op, 1)

    @classmethod
    def is_rotation(cls, op):
        """ check whether a operator is rotation gate.

        if True => means that should solve the op.angle.
        
        """
        # get original op_type
        if op not in cls.op_type_map:
            op = cls.convert_type(op, True)

        return op in cls.rotation_gates