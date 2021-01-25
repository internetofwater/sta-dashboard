from datetime import datetime


# def extract_date(resultTimeString, return_format='datetime'):
#     # Example datetime format: '1954-09-10T12:00:00.000Z/2019-12-13T21:26:00.000Z'
#     assert len(resultTimeString) == 49

#     year = [s[:10] for s in resultTimeString.split('/')]
#     startDate, endDate = year[0], year[1]

#     if return_format == 'str':
#         return startDate, endDate
#     elif return_format == 'datetime':
#         assert len(startDate) == 10
#         assert len(endDate) == 10
#         return dt.strptime(startDate, "%Y-%m-%d"), dt.strptime(endDate, "%Y-%m-%d")


# def compare_date(dataDateTuple: tuple, queryDateTuple: tuple) -> bool:
#     dataStartDate, dataEndDate = dataDateTuple
#     queryStartDate, queryEndDate = queryDateTuple
#     return dataStartDate <= queryStartDate and dataEndDate >= queryEndDate


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
