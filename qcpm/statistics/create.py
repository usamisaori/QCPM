import csv


def create(csvpath, metric):
    """ create csv file with header line
    
    """
    with open(csvpath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')

        header = [
            'Filename',
            'Size(number of gates)', '', '', '',
            metric.title(), '', '', '', # Cycle / Depth
            'SQGs', '', '', '',
            'MQGs', '', '', '',
            'Total Time'
        ]

        writer.writerow(header)

        subHeader = [
            '',
            'before', 'after', 'reduce', '',
            'before', 'after', 'reduce', '',
            'before', 'after', 'reduce', '',
            'before', 'after', 'reduce', '',
            ''
        ]

        writer.writerow(subHeader)