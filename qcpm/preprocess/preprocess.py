import os

from qcpm.operator import Operator


def preprocess(path, ext='.qasm'):
    """ preprocess of QASM file.

    work as a generator.
    preprocess each line(gate operation) like "cx q[2],q[4];"
        into a Operator object and <yield> it.

    Args:
        path: file path
        ext: extension name, deafult '.qasm' 
    """
    path = path + ext if os.path.splitext(path)[-1] == '' else path
    
    with open(path, 'rt') as file:
        # Skip the first two lines
        # Skip => OPENQASM 2.0; include "qelib1.inc"; 
        header = [next(file), next(file)]
        flag = True

        for line in file:
            # "cx q[2],q[4];" => 'cx', 'q[2],q[4]'
            # Caution!: "cx q[2], q[4];" => 'cx', 'q[2],', 'q[4]'
            # Caution!: "u2(pi / 2, - pi / 2) q[0];" => 'u2(pi/2,-pi/2)', 'q[0]'
            # 
            # thus *operands may be 'q[2],q[4]' or ['q[2],', 'q[4]']
            
            # "u2(pi / 2, - pi / 2) q[0];" => "u2(pi/2,-pi/2)q[0]" 
            _line = line.strip().replace(' ', '')[:-1]
            left_bound = _line.index('[') - 1

            # "u2(pi/2,-pi/2)q[0]" => u2(pi/2,-pi/2)
            op_type = _line[:left_bound]
            # "u2(pi/2,-pi/2)q[0]" => q[0]
            operands = _line[left_bound:]
            # print(f'op_type: {op_type}, operands: {operands}')

            try:
                op = Operator(op_type, operands)

                if flag:
                    # no error occur => header info is all gathered
                    # should yeild it.
                    flag = False
                    yield header

                yield op
            
            except ValueError:
                # "qreg q[];" will occur this error
                # keep it in header
                header.append(line)