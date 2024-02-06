import requests
from datetime import datetime
from emby_actions import emby_get_items, emby_update_items
from store_details import sqlite_create_store_table, sqlite_load_rating_details


sqlite_store = "imdb_ratings.db"
sqlite_create_store_table(sqlite_store)

items = emby_get_items()
prem_date_window = 60*60*24*30 # 30 days

changed_items = []
for item in items:
    #print(item)
    name = item["Name"]
    emby_id = item["Id"]
    type = item["Type"]
    prem_date = item.get("PremiereDate", "1900-01-01")
    prem_date = prem_date.split("T")[0]    
    community_rating = item.get("CommunityRating", 0)
    prem_date_obj = datetime.strptime(prem_date, "%Y-%m-%d")
    diff = datetime.now() - prem_date_obj
    imdb_id = item["ProviderIds"].get("Imdb", None)
    if not imdb_id: imdb_id = item["ProviderIds"].get("IMDB", None)
    if type == "Movie" or diff.total_seconds() < prem_date_window:
        if imdb_id:
            rating_details = sqlite_load_rating_details(sqlite_store, imdb_id)
            if rating_details is not None:
                store_imdb_rating = float(rating_details["rating"])
                if store_imdb_rating != community_rating:
                    print("Ratings dont match : %s (%s -> %s) - %s" % (imdb_id, community_rating, store_imdb_rating, name))
                    changed_items.append({"Id": emby_id, "Type": "CommunityRating", "Value": store_imdb_rating})
                #else:
                    #print("Ratings match : %s (%s)" % (imdb_id, community_rating))
            else:
                print("Not found in store : %s - %s" % (imdb_id, name))
        else:
            print("Emby item has no Imdb : (%s) %s" % (emby_id, name))

changed_count = len(changed_items)
print("Change item count : %s" % (changed_count,))
if(changed_count > 0):
   emby_update_items(changed_items)
