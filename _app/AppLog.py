
from datetime import datetime

max_rows = 5
rows = []


class AppLog:
    def __init__(self) -> None:
        pass

    def log(str) -> None:
        dt = datetime.now()
        str = f"{dt.year:04}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:06.3}::{str}"
        print(str)
        rows.append(str)
        if len(rows) > max_rows:
            rows.pop(0)

    def __str__(self) -> str:
        return "\n".join(rows)
