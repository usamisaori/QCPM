import csv

from qcpm.statistics.info import gatherInfo

# header = [
#     'Filename',
#     'Size(number of gates)', '', '',
#     metric.title(), '', '', # Cycle / Depth
#     'SQGs', '', '',
#     'MQGs', '', '',
#     'Total Time'
# ]


def addRow(csvpath, filename, circuitInfos, metric, time):
    """ create csv-row and append it

    """
    info = gatherInfo(circuitInfos, metric)

    keys = ['size', metric, 'SQG', 'MQG']
    data = []
    for key in keys:
        data.append(info[f'before_{key}'])
        data.append(info[f'after_{key}'])
        data.append(info[f'reduce_{key}'])
        data.append('')

    with open(csvpath, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')

        writer.writerow([
            filename, 
            *data,
            time
        ])