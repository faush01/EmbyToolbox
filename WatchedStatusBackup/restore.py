import os
import json
from emby_client import check_server, get_user_list, get_user_items, set_watched


with open("config.json", 'r') as f:
    config = json.load(f)

print ("Emby Server           : %s" % config["emby_server"])
print ("ApiKey                : %s" % config["api_key"])
print ("Backup Path           : %s" % config["output_path"])

check_server(config)
user_list = get_user_list(config)

for user in user_list:
    print(user["Name"])
    backup_path = os.path.join(config["output_path"], "watched-" + user["Name"] + ".txt")

    if not os.path.exists(backup_path):
        print("No backup data for : %s" % user["Name"])
        continue
    watched_items = []
    with open(backup_path, 'r') as f:
        for line in f:
            watched_items.append(line.rstrip())
    user_items = get_user_items(config, user["Id"])
    #print(user_items)
    count = 0
    total = float(len(watched_items))
    last_percentage = -1
    for item_key in watched_items:
        if item_key in user_items:
            item_id = user_items[item_key]
            set_watched(config, user["Id"], item_id)
        percent_done = int((count / total) * 100)
        count += 1
        percent_disp = percent_done % 5 == 0
        if percent_disp and last_percentage != percent_done:
            last_percentage = percent_done
            print("Processed : %s%%" % percent_done)
    print("Processed : %s%%" % 100)
