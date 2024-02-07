import requests
import os
import time
from datetime import datetime
from emby_actions import emby_get_items

items = emby_get_items()
prem_date_window = 60*60*24*30 # 30 days
count = 0

with open("imdb_ids.csv", "w") as file:
    for item in items:
        name = item["Name"]
        type = item["Type"]
        prem_date = item.get("PremiereDate", "1900-01-01")
        prem_date = prem_date.split("T")[0]
        prem_date_obj = datetime.strptime(prem_date, "%Y-%m-%d")
        diff = datetime.now() - prem_date_obj
        if type == "Movie" or diff.total_seconds() < prem_date_window:
            imdb_id = item["ProviderIds"].get("Imdb", None)
            if not imdb_id: imdb_id = item["ProviderIds"].get("IMDB", None)
            if imdb_id:
                #print("Name : %s (%s)" %(name, imdb_id))
                line = "%s,%s\n" % (imdb_id, prem_date)
                file.write(line)
                count += 1

print("Emby item count : %s" % (count))
