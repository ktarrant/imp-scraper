from datetime import datetime

def guess_year(month, day):
    today = datetime.today()
    year = today.year if month >= today.month else (today.year + 1)
    return year