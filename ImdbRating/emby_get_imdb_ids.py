import requests
import os
import time


emby_url = os.environ.get('emby_url')
api_key = os.environ.get('api_key')
url = emby_url
url += "/emby/Items"
url += "?Recursive=True"
url += "&IncludeItemTypes=Movie,Episode" # Movie,Episode
url += "&Fields=ProviderIds,PremiereDate"
url += "&ImageTypeLimit=0"
url += "&api_key=" + api_key

print("URL: %s" % url)
time.sleep(5)

result = requests.get(url)
items = result.json()["Items"]

with open("imdb_ids.csv", "w") as file:
    for item in items:
        name = item["Name"]
        prem_date = item.get("PremiereDate", "1900-01-01")
        imdb_id = item["ProviderIds"].get("Imdb", None)
        if imdb_id and prem_date:
            prem_date = prem_date.split("T")[0]
            #print("Name : %s (%s)" %(name, imdb_id))
            line = "%s,%s\n" % (imdb_id, prem_date)
            file.write(line)
    