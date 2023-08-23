import pkgutil
import json
from collections import deque

from qcpm.migration.pattern import MigrationPattern 


class Migrater:
    """ Callable object that map migration patterns on operators.

    Migrater works just like Invoker(Reducer/..) in qcpm.optimization 

    """
    def __init__(self, source_type, target_type):
        # patterns data => self.rules
        # 1. when [source_type]_to_[target_type] doesn't esist.
        # 2. if we have 'IBM_to_Surface.json', we can also load 'Surface_to_IBM'
        #       by just swapping the src/dst in loaded self.rules
        # 
        # print(f'Try to migration from {source_type} to {target_type}')

        swap = False
        try:
            path = f'/rules/{source_type}_to_{target_type}.json'
            data = pkgutil.get_data(__package__, path)
        except FileNotFoundError:
            # For example: if we just give 'IBM_to_Surface.json'
            # when try to load 'Surface_to_IBM.json', [FileNotFoundError] occur!
            # 
            # but we can change to load 'IBM_to_Surface.json'
            # and then swap loaded data's src/dst.
            # 
            swap = True
            path = f'/rules/{target_type}_to_{source_type}.json'
            data = pkgutil.get_data(__package__, path)

        self.rules = json.loads(data.decode())
        if swap:
            self.rules = [ {'src': rule['dst'], 'dst': rule['src']} 
                for rule in self.rules]

        self.patterns = [ MigrationPattern(**rule) for rule in self.rules ]
        

        # the max/min size of operator need to match in all patterns
        self.min_size = len(min(self.rules, key=lambda rule:len(rule['src']))['src'])
        self.max_size = len(max(self.rules, key=lambda rule:len(rule['src']))['src'])

    def __call__(self, ops):
        """
        thus Migrater is callable like Invoker.
        but Migrater will not change the input ops and
        just generate operators(migration version)

        Args:
            ops: List of Operator, also may Circuit object
        """
        if len(ops) < self.min_size:
            return []

        for pattern in self.patterns:
            # not like ReductionPattern, 
            # MigrationPattern.map will return list of Operators 
            yield from pattern.map(ops)


def migrate(operators, source_type, target_type):
    """ QASM code migrate: from [source_type] to [target_type]

    work as a generator to generates transfered operators

    Args:
        operators: list of Operator (or Circuit object).
        source_type: eg. 'IBM'
        target_type: eg. 'Surface'
    
    """    
    buffer = deque()
    migrater = Migrater(source_type, target_type)

    for operator in operators:
        buffer.append(operator)

        # if rule_min_size = 2, rule_max_size = 5
        # -------------------------
        # Case 1. ['h'] => Nothing
        # Case 2. ['(h)hShsh'] => popleft()
        # Case 3. ['hsh'] => migrater(['hsh'])

        if len(buffer) > migrater.max_size:
            yield buffer.popleft()
        
        if len(buffer) >= migrater.min_size:
            # recall that Migrater.__call__() will return list of Operator
            yield from migrater(buffer)

    # yield the left operators
    while len(buffer) != 0:
        yield buffer.popleft()