from multiprocessing.sharedctypes import Value
import numpy as np


def sample(targets, probabilities):
    """ sample a element with [probabilities] in [target]

    Args:
        targets: eg. ['a', 'b', 'c', 'd']
        probabilities: eg. [0.1, 0.2, 0.3, 0.4]
            probabilities should guarantee that sum = 1
    -------
    Returns:
        Sample a element in targets according to probabilities. 
    """
    # First:
    # [0.1, 0.2, 0.3, 0.4] => [0.1, 0.3, 0.6, 1.0]
    # 
    prob = probabilities[0]
    probs = [ prob ]

    for i in range(1, len(probabilities)):
        prob += probabilities[i]
        probs.append(prob)

    # Second:
    # eg.
    # ['a', 'b', 'c', 'd'] with [0.1, 0.3, 0.6, 1.0]
    # if p = 0.45 => < 0.6 that choose 'c'
    # 
    p = np.random.rand()

    for i, prob in enumerate(probs):
        if p <= prob:
            return targets[i] 


class Simulation:
    """ Monte Carlo simulation

    """
    def __init__(self, searcher):
        self.searcher = searcher

    def gatherCandidates(self, candidate):
        """ return the cnadidates after candidate in SIMULATION_SIZE

        thus the simulation will randomly choose candidate in the candidates
        that return by gatherCandidates.

        """
        targets = []
        circuit = self.searcher.circuit
        candidates = self.searcher.candidates

        # index of current candidate in all candidates
        index = candidates.index(candidate)
        # range limit of simulation
        limit = candidate.begin + self.searcher.SIMULATION_SIZE
        if limit > len(circuit):
            limit = len(circuit)
        
        for i in range(index + 1, len(candidates)):
            # filter candidate in simulation range
            # -----------
            # eg. candidate: [1, 4, 7] thus end = 7
            # should gather the candidates that guarantee end < limit above.
            if candidates[i].end < limit:
                targets.append(candidates[i])
        
        return targets


    def __call__(self, candidate):
        """ simulate one candidate to get value

        simulate candidate in SIMULATION_SIZE and SIMULATION_TIMES.

        Args:
            candidate: one Candidate object
        -------
        Returns:
            value: simulation result of this candidate.
        """
        values = []

        # for each simulation turn
        for _ in range(self.searcher.SIMULATION_TIMES):
            # list of candidate that could shoose to simualte.
            targets = self.gatherCandidates(candidate)

            # list of candidate that already choose to apply.
            applied = [ candidate ]
            value = candidate.delta(self.searcher.metric, self.searcher.circuit)

            # filter that guarantee there is no conflict with current candidate
            targets = list(filter(lambda c: not (c & applied), targets))
            
            # start simulation
            while len(targets) != 0:
                # Step 1. calculate probabilities acoording to saving of each candidate
                probs = [ t.delta(self.searcher.metric, self.searcher.circuit) for t in targets ]
                probs = [1] if len(probs) == 1 else np.array(probs) / sum(probs)

                # Step 2. sample a candidate
                selected = sample(targets, probs)
                targets.remove(selected)
                

                # Step 3. decide to apply it => calculate delta value
                applied.append(selected)
                value += selected.delta(self.searcher.metric, self.searcher.circuit)
                
                # Step 4. update candidates that guarantee that selected one 
                # will not be conflict with candidates in [candidates].  
                targets = list(filter(lambda c: not (c & applied), targets))
            
            # end of one simualtion turn.
            values.append(value)

        return np.mean(values)
