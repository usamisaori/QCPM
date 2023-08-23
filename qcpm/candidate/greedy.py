from qcpm.candidate.plan import Plan, Plans


def GreedySearchPlan(circuit, candidates, metric):
    """ filter candidates(without conflict occurance) and generate Plans.

    args are corresponding to the args in SearchPlan(circuit, candidates, metric):

    Args: 
        circuit: Circuit object, just may be used in calculate delta_depth.
        candidates: list of Candidate object.
        metric: cycle or depth which used to calculate value of candidate.
    -------
    Returns:
        Plans object contains <ALL> possible mapping plans.
    """
    count = 0 # plan's total number
    size = len(candidates)
    plans = []

    if size != 0:
        target = candidates[0]
        temp = [target]
        s = set(target.pos) # eg. like {1, 4}
        delta_cost = target.delta(metric, circuit)

        for j in range(1, size):
            # if no conflict => add this candidate
            if not (candidates[j] & s):
                temp.append(candidates[j])
                delta_cost += candidates[j].delta(metric, circuit)
                # eg. [1, 4] no conflict with [3, 7]
                #   => {1, 4} | {3, 7} => {1, 3, 4, 7}
                # 
                s = s | set(candidates[j].pos)
        
        count += 1

        # generate new Plan.
        plans.append(
            Plan(temp, delta_cost)
        )

    # generate Plans object and return.
    plans = Plans(plans)
    print(plans)

    return plans