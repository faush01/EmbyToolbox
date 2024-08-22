import sys, json
from store_details import sqlite_load_rating_details, sqlite_delete_rating_details, sqlite_list_all

command = sys.argv[1]

if command == "show":
    item_data = sqlite_load_rating_details("imdb_ratings.db", sys.argv[2])
    print (json.dumps(item_data, indent=4))

elif command == "delete":
    imdb_list = sys.argv[2].split(",")
    del_count = sqlite_delete_rating_details("imdb_ratings.db", imdb_list)
    print (f"Deleted {del_count} items")

elif command == "list":
    imdb_id_list = sqlite_list_all("imdb_ratings.db")
    print(imdb_id_list)

else:
    print("Unknown command")

