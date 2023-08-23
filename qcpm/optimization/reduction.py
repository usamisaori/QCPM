from collections import deque

from qcpm.optimization.invoker import Reducer


_reductions = {
   # should be set by getReductions(when first call)
   # For example: 
   # "IBM": [ Reducer('reversible'), Reducer('hadamard') ]   
}

##########################
#                        #
#     Tool Functions     #
#                        #
##########################

def getMaxRuleSize(reductions):
    """
    Args:
        reductions: [...] reduction runners
    -------
    Returns: 
        max_rule_size
    """
    max_sizes = []

    for reduction in reductions:
        max_sizes.append( reduction.max_size )
    
    return max(max_sizes)

# should be set by getReductions(system) like:
# _rule_size_max = getMaxRuleSize(_reductions)
_rule_size_max = 0

def getReductions(system):
    """ getReductions according to the system

    init Reductions when first call it.
    else return the memoized reductions by system

    Args:
        system: 'IBM' / 'Surface' etc.
    -------
    Returns:
        reductions: list of Reducer
    """
    if system in _reductions:
        return _reductions[system]

    # each rule corresponding to a Reducer
    reduction_rules = ['reversible', 'hadamard']
    reductions = []

    # init Reducers
    for rule in reduction_rules:
        reductions.append( Reducer(rule, system) )

    # update global _reductions and _rule_size_max
    _reductions[system] = reductions

    global _rule_size_max
    _rule_size_max = getMaxRuleSize(_reductions[system])

    return _reductions[system]


###############################
#                             #
#     Reduction Generator     #
#                             #
###############################

def reduction(operators, system='IBM'):
    """ Reduction Generator.

    apply Reduction Pattern Mapping and yield the Operator after mapping.

    Args:
        operators: list of Operator / 
            or a generator which generates Operator thus can compose to be a pipe.
        system: 'IBM' / 'Surface' etc.
    """
    buffer = deque()
    reductions = getReductions(system)

    for operator in operators:
        buffer.append(operator)

        # if rule_min_size = 2, rule_max_size = 5
        # -------------------------
        # Case 1. ['h'] => Nothing
        # Case 2. ['(h)hShsh'] => popleft()
        # Case 3. ['hsh'] => reduction(['hsh'])

        if len(buffer) > _rule_size_max:
            yield buffer.popleft()

        for reductionRule in reductions:
            # remember that reduction will change buffer's size
            if len(buffer) >= reductionRule.min_size:
                reductionRule(buffer)
        
    # yield the left Operators
    while len(buffer) != 0:
        yield buffer.popleft()