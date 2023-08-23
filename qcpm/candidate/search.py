import random

from qcpm.candidate.simulation import Simulation
from qcpm.candidate.plan import Plan, Plans


##########################
#                        #
#      Log Functions     #
#                        #
##########################

def logger(searcher):
    """ print log data

    Args:
        searcher: [self] of Searcher instance
    Returns:
        log: contains log functions:
            => call like: log('targets')(targets)

    
    """
    logpath = 'plan.txt'
    logdata = ''

    def startFunc():
        nonlocal logdata

        logdata = '' # reset logdata
        s = 'Monte Carlo-based plan searching\n\n'
        s += '-' * 12 + '\n\n'

        logdata += s

    def targetsFunc(targets):
        nonlocal logdata

        s = f'Expansion: Candidates size: {len(targets)}\n\n'
        for target in targets:
            s += str(target)
            s += '\n'
        
        logdata += s

    def selectedFunc(target):
        nonlocal logdata

        # log:
        # ----------
        # Selected: Pos: [40, 42] xx => I
        # ... xchxcxccch ...
        # 
        s = f'\nSelected: {target}\n'
        s += '    ... '

        end = searcher.pos + searcher.WINDOW_SIZE
        if end > len(searcher.circuit):
            end = len(searcher.circuit)
        for i in range(searcher.pos, end):
            s += searcher.circuit.draft[i]
        s += ' ... \n'

        logdata += s

        # log:
        # ----------
        # target:    ^ ^
        #
        s = ' ' * (end - searcher.pos)
        s = list(s)
        try:
            for index in target.pos:
                s[index - searcher.pos] = '^'
        except:
            pass
        s = 'target: ' + ''.join(s) + '\n'
        s += '\n' + '-' * 10

        logdata += s + '\n\n'

    def planFunc(selected):
        nonlocal logdata

        s = 'Complete Plan: \n\n'
        plan = '\n'.join([str(candidate) for candidate in selected])
        s += plan + '\n'
        s += f'\nTotal Saving: {searcher.saving}\n\n'

        logdata += s

    def endFunc(toFile=False):
        if toFile:
            with open(logpath, 'w') as f:
                f.write(logdata)
        else:
            print(logdata)

    ##############################################

    def log(key):
        logs_dict = {
            'start': startFunc,
            'targets': targetsFunc,
            'selected': selectedFunc,
            'plan': planFunc,
            'end': endFunc
        }

        return logs_dict[key]

    return log

############################
#                          #
#     Class Definition     #
#                          #
############################

class SearchPlan:
    """ Monte Carlo-based plan searching
    
    callable class:
        searchPlan(circuit, candidates)() => return Plans.

    Remember: after selecting each candidate:
        => candidate.apply(circuit); circuit.update()
    
    """
    WINDOW_SIZE = 20
    SIMULATION_SIZE = 10
    SIMULATION_TIMES = 10

    def __init__(self, circuit, candidates, metric):
        """
        Args:
            circuit: Circuit object.
                    =>
                operators / draft.
            candidates: sorted list of Candidate object.
                    =>
                pos: eg. [1, 4]
                pattern: eg. pattern.src/dst => {'operator': 'xx', 'operands': 'aa'}
            metric: cycle or depth which used to calculate value of candidate.
        """
        self.circuit = circuit
        self.candidates = candidates
        self.metric = metric

        self.log = logger(self)

    def expansion(self):
        """ Expanase to get targte candidates

        Expanase target candidates from start.

        Returns:
            targets: list of Candidates with conflict from beginning one.
                => [!Caution]: targets may be empty
        """ 
        cur = 0 # candidates' cur

        while True:
            # reach the end of all candidates.
            # means no target candidates
            if cur == len(self.candidates):
                return []
            
            # ignore the after candidates that 
            # conflict with current selected candidates
            if self.candidates[cur] & self.selected:
                cur += 1
            else:
                break

        # current candidate => candidates[cur]
        targets = [ self.candidates[cur] ]

        # gather the candidates that have conflicts with current candidate.
        #   => self.candidates[i] & targets[0]
        for i in range(cur + 1, len(self.candidates)):
            if self.candidates[i] & targets[0]:
                targets.append(self.candidates[i])
            else:
                break
        
        return targets
    
    def simulation(self, candidates):
        """ simulation to evaluate value of each candidate.

        Args:
            candidates: list of Candidate object.
        -------
        Returns:
            values: list of int value
        """
        return [ Simulation(self)(candidate) + candidate.delta(self.metric, self.circuit) 
                    for candidate in candidates ]
    
    def reset(self):
        """ reset searcher's states

        """
        # operator position in circuit
        ## will change at Step 3 in __call__
        self.pos = 0

        # will change at Step 3 in __call__
        self.saving = 0 # total saving for selected plan
        self.selected = [] # should contains all selected candidates

    def __call__(self):
        """ Monte Carlo-based plan searching

        Returns:
            Plans object contains all possible plan.
        """
        # Step 0. reset searcher's state
        self.reset()

        self.log('start')()
        while len(self.candidates) != 0:
            # Step 1. select and expansion candidates
            targets = self.expansion()

            self.log('targets')(targets)

            # Step 2. Select and apply candidate
            ## no more targets => stop searching.
            if len(targets) == 0:
                break
            ## if no conflict => apply 
            elif len(targets) == 1:
                target = targets[0]
            ## else candidates with conflict => simulate
            else:
                values = self.simulation(targets)
                # choose the target with max value
                # ! values may be the same, should randomly choose one
                max_value = max(values)
                max_values = list(filter(lambda x:x == max_value, values))
                max_index = random.randint(0, len(max_values) - 1)
                target = targets[max_index]
            
            self.pos = target.begin
            
            self.log('selected')(target)

            # Step 3. Apply selected candidate
            ## append selected candidate to self.selected
            ## real call will delay to self.plans.best().apply(circuit) in mapper
            self.selected.append(target)
            self.saving += target.delta(self.metric, self.circuit)
            self.pos = target.end + 1

            # Step 4. filter candidates that guarantee 
            # there is no conflict with target.
            filter(lambda candidate: not (candidate & target), self.candidates)

        self.log('plan')(self.selected)
        self.log('end')()

        return Plans([ Plan(self.selected, self.saving) ])