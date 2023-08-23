def calculateReduce(before, after):
    reduce = before - after

    if reduce == 0:
        reduceRate = '-'
    else:
        reduceRate = f'{reduce / before * 100:.2f}%'

    return f'{reduce}({reduceRate})'


def gatherInfo(circuitInfos, metric):
    """ gather info which used to create row and return info dict.
    
    """
    before, after = circuitInfos
    data = dict()

    # 1. size
    before_size = before.size
    after_size = after.size

    data['before_size'] = before_size
    data['after_size'] = after_size
    data['reduce_size'] = calculateReduce(before_size, after_size)

    # 2. metric - cycle / depth
    if metric == 'cycle':
        before_cycle = before.cycle
        after_cycle = after.cycle

        data['before_cycle'] = before_cycle
        data['after_cycle'] = after_cycle
        data['reduce_cycle'] = calculateReduce(before_cycle, after_cycle)

    elif metric == 'depth':
        before_depth = before.depth
        after_depth = after.depth

        data['before_depth'] = before_depth
        data['after_depth'] = after_depth
        data['reduce_depth'] = calculateReduce(before_depth, after_depth)

    # 3. SQG
    before_SQG = before.SQG_num
    after_SQG = after.SQG_num

    data['before_SQG'] = f'{before_SQG}({",".join(before.SQG)})'
    data['after_SQG'] = f'{after_SQG}({",".join(after.SQG)})'
    data['reduce_SQG'] = calculateReduce(before_SQG, after_SQG)

    # 4. MQG
    before_MQG = before.MQG_num
    after_MQG = after.MQG_num

    data['before_MQG'] = f'{before_MQG}({",".join(before.MQG)})'
    data['after_MQG'] = f'{after_MQG}({",".join(after.MQG)})'
    data['reduce_MQG'] = calculateReduce(before_MQG, after_MQG)

    return data