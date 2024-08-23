import requests
from datetime import datetime
from emby_actions import emby_get_items, emby_update_items
from store_details import sqlite_create_store_table, sqlite_load_rating_details, load_emby_items


num_days = 120

sqlite_store = "imdb_ratings.db"
sqlite_create_store_table(sqlite_store)

emby_items = load_emby_items("emby_items.tsv")

prem_date_window = 60 * 60 * 24 * num_days

changed_items = {}
for item in emby_items:

    #print(item)
    name = item["name"]
    emby_id = item["emby_id"]
    type = item["type"]
    prem_date = item["prem_date"]
    community_rating = item["rating"]
    prem_date_obj = datetime.strptime(prem_date, "%Y-%m-%d")
    diff = datetime.now() - prem_date_obj
    imdb_id = item["imdb_id"]

    if type == "Movie" or diff.total_seconds() < prem_date_window:
        rating_details = sqlite_load_rating_details(sqlite_store, imdb_id)
        if rating_details is not None:
            store_imdb_rating = float(rating_details["rating"])
            emby_rating = float(community_rating)
            rating_diff = int(store_imdb_rating * 10) - int(emby_rating * 10)
            if rating_diff != 0:
                print("Ratings dont match : %s (%s -> %s) - %s" % (imdb_id, community_rating, store_imdb_rating, name))
                changed_items[emby_id] = [{"Type": "CommunityRating", "Value": store_imdb_rating}]
            #else:
                #print("Ratings match : %s (%s)" % (imdb_id, community_rating))
        else:
            print("Not found in store : %s - %s" % (imdb_id, name))

#print(changed_items)
changed_count = len(changed_items)
print("Change item count : %s" % (changed_count,))
if(changed_count > 0):
   emby_update_items(changed_items)
