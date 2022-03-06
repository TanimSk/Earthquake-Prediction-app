from plyer import notification
from time import sleep
from jnius import autoclass
from pytz import timezone
from datetime import datetime
import csv


def get_csv(thisDate):
    data_frame = csv.reader(open('./files/records.csv', "r"), delimiter=",")
    minor_ratings = "Not Found"
    severe_ratings = "Not Found"

    for row in data_frame:
        if thisDate == row[0]:
            minor_ratings = row[1]
            severe_ratings = row[2]
            break

    return minor_ratings, severe_ratings


if __name__ == '__main__':
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)
    while True:
        with open("./files/today_date.txt", 'r') as f:
            today_date = f.read()

        date_obj = datetime.now(timezone('UTC')).astimezone(
            timezone('Europe/London'))

        dateBD = date_obj.strftime("%d")

        if not today_date == dateBD:
            with open("./files/today_date.txt", 'w') as f:
                f.write(dateBD)

            minor, severe = get_csv(str(date_obj.strftime("%Y-%m-%d")))

            if not severe == "":
                severe = "🔴" + severe

            notification.notify(
                title="Todays Update",
                message=f"🟡{minor} {severe}",
                app_name="Earthquake Predictor",
                timeout=5,
                ticker="Todays Update",
                toast=False
            )
        sleep(3600)
