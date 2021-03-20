import csv
from datetime import datetime, timedelta
from os import remove
from typing import List, Union


class BotChat:
    def __init__(self, dbname: str, clean_in: int = 15):
        if not dbname.endswith(".csv"):
            dbname += ".csv"
        self.db = f"userge/xcache/{dbname}"
        self.expire = clean_in
        try:
            self.clean()
        except Exception:
            self.drop()

    def store(self, msg_id: int, user_id: int) -> None:
        expiry = datetime.timestamp(datetime.now() + timedelta(days=self.expire))
        with open(self.db, "a+", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow([msg_id, user_id, int(expiry)])

    def search(self, msg_id: int = None) -> Union[int, List, None]:
        with open(self.db, "r") as csvfile:
            reader = csv.reader(csvfile)
            if msg_id:
                for x in reversed(list(reader)):
                    # not the best way to do that but works :)
                    # Still better than reversing the whole file imo
                    if x[0] == str(msg_id):
                        # LOG.info("SUCCESS !")
                        return int(x[1])
                # LOG.info("No Matches Found ...")
            else:
                return list(reader)

    def drop(self) -> None:
        try:
            remove(self.db)
        except OSError:
            pass
        #     LOG.info("Nothing found to cleared.")
        # else:
        #     LOG.info("Database cleared Successfully.")

    def clean(self) -> bool:
        if not (data_ := self.search()):
            # LOG.error("No Data Found to clean !")
            return False
        t_now = int(datetime.timestamp(datetime.now()))
        lines = list(filter(lambda x: bool(int(x[-1]) > t_now), data_))
        with open(self.db, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerows(lines)
        # LOG.error(f"Message data from last {self.expire} Days have been cleared")
        return True
