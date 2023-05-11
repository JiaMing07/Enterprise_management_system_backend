import datetime

def get_timestamp():
    return (datetime.datetime.now()).timestamp()

def get_date():
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return dt