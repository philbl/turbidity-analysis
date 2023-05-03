import pandas
from datetime import datetime


def convert_string_date_to_datetime(date_string: str) -> datetime:
    """
    Convert a String of 16 or 19 caracters to datetime
    String must be in format of "%Y-%d-%m %H:%M" or "%Y-%d-%m %H:%M:%S"
    """
    if len(date_string) == 16:
        date = datetime.strptime(date_string, "%Y-%d-%m %H:%M")
    elif len(date_string) == 19:
        date = datetime.strptime(date_string, "%Y-%d-%m %H:%M:%S")
    else:
        raise ValueError
    return date


def load_and_clean_data(csv_path: str) -> pandas.DataFrame:
    """
    Load csv data with ";" delimeter. Rename coloumns with lower caracters.
    The turbidity and temp value have a ",". We want to replace it with a "." so it
    can be float.
    Date is also converted
    """
    data = pandas.read_csv(csv_path, delimiter=";")
    data.columns = [col.lower() for col in data.columns]
    data["turbidity"] = (
        data["turbidity"].apply(lambda string: string.replace(",", ".")).astype(float)
    )
    data["temp"] = (
        data["temp"].apply(lambda string: string.replace(",", ".")).astype(float)
    )
    data["date"] = data["date"].apply(convert_string_date_to_datetime)
    return data
