from random import randint, uniform
from datetime import datetime, timedelta
import pandas as pd


def createData(nb_rows, NB_DAYS:int=15, NB_DELAY_TIME:int=360) -> list:
    """
    Retourne une liste avec toutes les messages est leurs timestamp
    :return: list[]
    """
    data = []
    NB_MSG_PER_DAY = nb_rows // NB_DAYS + 1
    date = datetime.today() - timedelta(days=NB_DAYS)  # NB_DAYS avant aujourd'hui
    total_rows = 0
    # print("nb_rows, NB_MSG_PER_DAY, date:", nb_rows, NB_MSG_PER_DAY, date)

    while not (total_rows >= nb_rows):
        delay = 0
        msg_per_day = randint(1, NB_MSG_PER_DAY*2)
        for i in range(msg_per_day):
            if total_rows >= nb_rows:
                break
            delay += uniform(0, NB_DELAY_TIME)
            data.append((date + timedelta(seconds=delay)).isoformat())
            total_rows += 1
        # print("\rdate, NB_MSG_PER_DAY, msg_per_day:", date, total_rows, msg_per_day, end="")
        date += timedelta(days=1)

    return data


def createFile(file, newfile="data.csv"):
    data = pd.read_csv(file)
    timestamps = createData(len(data))
    data['timestamps'] = timestamps
    data = data[['timestamps'] + list(data.columns[data.columns != 'timestamps'])]
    data.to_csv('time_'+newfile, index=False)


if __name__ == "__main__":
    file = "dataset\\twitter_dataset_copy.csv"
    createFile(file, "twitter_dataset_copy.csv")

