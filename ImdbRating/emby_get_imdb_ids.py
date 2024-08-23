import requests
import os
import time
from datetime import datetime
from emby_actions import emby_get_items

num_days = 120

items = emby_get_items()
prem_date_window = 60 * 60 * 24 * num_days
count = 0

with open("emby_items.tsv", "w") as file:
    for item in items:
        
        # extract some details
        emby_id = item["Id"]
        community_rating = item.get("CommunityRating", 0)

        name = item["Name"]
        type = item["Type"]
        if type == "Episode":
            name = ("%s - %s - S%sE%s" % (item["SeriesName"], name, item["ParentIndexNumber"], item["IndexNumber"]))   
             
        prem_date = item.get("PremiereDate", "1900-01-01")
        prem_date = prem_date.split("T")[0]
        prem_date_obj = datetime.strptime(prem_date, "%Y-%m-%d")
        diff = datetime.now() - prem_date_obj
        
        imdb_id = item["ProviderIds"].get("Imdb", None)
        if not imdb_id: imdb_id = item["ProviderIds"].get("IMDB", None)        

        # select what we want
        if imdb_id and (type == "Movie" or diff.total_seconds() < prem_date_window):
            line = "%s\t%s\t%s\t%s\t%s\t%s\n" % (emby_id, imdb_id, prem_date, type, community_rating, name)
            file.write(line)
            count += 1

print("Emby item count : %s" % (count))
