from qcpm.optimization.reduction import reduction
from qcpm.optimization.commutation import commutation


def optimizer(operators, system):
    """ Optimizer which call both the reduction and commutation.

    Optimizer steps: reduce -> commutate

    Example: 
        call: optimizer(preprocess(path))
    Args:
        operators: list of Operator object / maybe Circuit object
        system: IBM / Surface ...
    """

    return commutation(
        reduction(
            operators, 
            system
        ),
        system
    )