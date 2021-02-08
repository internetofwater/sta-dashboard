from datetime import datetime


def extract_date(startDateString, endDateString):
    if len(startDateString[1:-1]) == 0:
        queryStartDate = datetime.min
    else:
        queryStartDate = datetime.strptime(
            startDateString[1:-1], '%Y-%m-%d')

    if len(endDateString[1:-1]) == 0:
        queryEndDate = datetime.max
    else:
        queryEndDate = datetime.strptime(
            endDateString[1:-1], '%Y-%m-%d')
    
    return queryStartDate, queryEndDate


def convert_date(isoDateString):
    return datetime.strptime(isoDateString, '%Y-%m-%dT%H:%M:%S.%fZ')
