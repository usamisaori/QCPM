import copy

from qcpm.migration.migrate import Migrater


def convert(source_patterns, target_system):
    """ convert patterns into target_system's form

    Args:
        source_patterns: IBM form patterns. 
            eg. 
            [
                {
                    "src": [ ["z", [0]], ["z", [0]] ],
                    "dst": []
                },
                ...
            ]
        target_system: for example: 'Surface'
    -------
    Returns:
        converted patterns:
            eg. 
            Recall that in Surface: z = xy
            [
                {
                    "src": [ ["x", [0]], ["y", [0]], ["x", [0]], ["y", [0]] ],
                    "dst": []
                },
                ...
            ]
    """
    migration_rules = Migrater('IBM', target_system).rules
    converted_patterns = []

    for pattern in source_patterns:
        # eg.
        # { "src": [ ["z", [0]], ["z", [0]] ], "dst": [] }
        for converted_pattern in _convert(pattern, migration_rules):
            converted_patterns.append(converted_pattern)
    
    return converted_patterns

def _convert(source_patten, rules):
    """ subroutine used in convert()

    convert one sinlge pattern by rules.
    may convert to several patterns.

    Args:
        source_pattern: eg. { "src": [ ["z", [0]], ["z", [0]] ], "dst": [] }
        rules: migration rules from Migrater()
            eg. [ ... { "src": [ ["z", [0]], "dst": [ ["x", [0]], ["y", [0]] ] } .. ]
    -------
    Returns:
        converted_patterns from this source_pattern. A List.
    """
    def solve(target):
        """
        target may be 'src'/ 'dst',
        eg. "src" =>  [
            ["h", [0]], ["s", [0]], ["h", [0]]
        ] # => call this is a [pattern], while call ["h", [0]] is a [operator]

        will reutrn the list of possible solved patterns:
        one of the patterns like:
        [
            ['ry', [0], '-pi/2'], ['z', [0]], 
            ['ry', [0], 'pi/2'], ['rx', [0], 'pi/2'], ['ry', [0], '-pi/2'], 
            ['ry', [0], '-pi/2'], ['z', [0]]
        ]

        cause of the gate may migrate to different compositions of gates like H:
        h = ry z = z ry = x ry
        returns are list of patterns corresponding to all possibility
        
        Args: 
            target: 'src' / 'dst'
        -------
        Returns:
            list of patterns
        """
        solved_patterns = [[]]

        # eg. target = 'src
        # source_pattern[target] = [ ["h", [0]], ["s", [0]], ["h", [0]] ]
        for operator in source_patten[target]:
            matched_operators = []

            # eg. operator = ["h", [0]]
            for rule in rules:
                # eg. rule: { "src": [ ["h", [0]], ["s", [0]], ["h", [0]] ], "dst": [...] }
                ok, pattern = _match(operator, rule)
                if ok:
                    matched_operators.append(pattern)
                    break
            
            # matched_operators is the list of operators
            #   => thus each elem in matched_operators is list of operator
            if len(matched_operators) == 0:
                matched_operators.append([operator])
            elif target == 'dst':
                matched_operators = matched_operators[:1]

            # find matched operators
            # Roughly explaination: 
            # 
            # for h = ry z = z ry = x ry, thus matched size: 3
            # if solved_patterns = [ pat1, pat2 ], after appending h operator:
            # should be: [ pat1+[ry z], pat1+[z ry], pat1+[x ry], pat2+[ry z] ... ]
            # 
            temp_patterns = []
            for i in range(len(solved_patterns)):
                for operators in matched_operators:
                    # if solved_patterns = [ pat1, pat2 ]
                    # copy the pat1 cause pat1 may have different possible successors
                    pattern = solved_patterns[i].copy()
                    # do pat1+[ry z] menthioned above
                    pattern.extend(operators)

                    temp_patterns.append(pattern)
            
            solved_patterns = temp_patterns

        return solved_patterns

    converted_patterns = []
    converted_src = solve('src')   
    converted_dst = solve('dst')

    # for example:
    # 
    # for origin rule: hsh => ShS
    # if h has 3 convertion choices, where s/S 1
    # 
    # then total possibility: 
    # 3 * 1 * 3 = 9 for [hsh] - src
    # and 1 * 3 * 1 = 3 for [ShS] - dst
    # Total: src * dst => 9 * 3 = 27 

    for src in converted_src:
        for dst in converted_dst:
            # Total possibility size: src * dst
            converted_patterns.append({
                'src': src,
                'dst': dst
            })

    return converted_patterns


def _match(operator, rule):
    """ match operator(with operands and angles) with rule

    Args:
        operator: eg. ["z", [0]] / ["ry", [1], "-pi/2"]
        rules: single migration rule from Migrater().rules
            eg. { "src": [ ["z", [0]] ], "dst": [ ["x", [0]], ["y", [0]] ] }
    -------
    Returns:
        ok => True: matched
        operators => if matched, return converted operators, like [ ["x", [0]], ["y", [0]] ] above
            should always be list of operator: [ [..,..], ... ]
    """
    # Step 1. test operator match
    # ------------------------------------
    # Assume that rule['src'] just contains one single operator
    if operator[0] != rule['src'][0][0]:
        return False, None 

    # Step 2. match! => books the operands
    # ------------------------------------
    LIMIT_QUBITS_NUM = 10 # limit just in patterns but not in the QASM circuit.
    books = [ -1 for i in range(LIMIT_QUBITS_NUM) ]

    # eg. operator: ["z", [2]], rule: ["z", [0]] => ["x", [0]], ["y", [0]]
    # should: => ["x", [2]], ["y", [2]]
    # 
    # so books[0] = 2
    for (convert_to_opd, input_opd) in zip(rule['src'][0][1], operator[1]):
        books[convert_to_opd] = input_opd

    # Step 3. change the operands in dst.
    # ------------------------------------
    # eg. "dst": [ ["x", [0]], ["y", [0]] ]
    dst = copy.deepcopy(rule['dst'])

    for i in range(len(dst)):
        # eg. ["x", [0]]
        # for i, opd in enumerate(operator[1]):
        #     operator[1][i] = books[opd]
        dst[i][1] = [ books[opd] for opd in dst[i][1] ]
    
    return True, dst[:]