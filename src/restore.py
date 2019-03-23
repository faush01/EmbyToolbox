
import sys
import json
from emby_client import authenticate, get_ulr_data, set_watched
from matcher import item_is_match

if len(sys.argv) == 1:
    print "Usage:"
    print "restore.py <backup file>"

backup_file = sys.argv[1]

print "Loading data from : %s" % backup_file

with open(backup_file, 'r') as f:
    backup_data = json.load(f)

config = backup_data["config"]

print "Emby Server : %s" % config.get("emby_server")
print "User Name   : %s" % config.get("user_name")
print "User Pass   : %s" % config.get("user_password")

user_info = authenticate(config)

print "AccessToken Token : %s" % user_info["AccessToken"]

url = ('{server}/emby/Users/{userid}/Items' +
       '?Recursive=true' +
       '&Fields=Path,ExternalUrls' +
       '&IsMissing=False'
       '&IncludeItemTypes=Movie,Episode' +
       '&ImageTypeLimit=0')

response_data = get_ulr_data(url, config, user_info)

item_list = response_data["Items"]
backup_items = backup_data["Items"]
count = 1
total = len(item_list)
last_percentage = 0

for item in item_list:

    item_found = None
    for backup_item in backup_items:
        if item_is_match(item, backup_item):
            item_found = backup_item
            break

    if item_found:
        played_current = item["UserData"]["Played"]
        played_backup = item_found["Played"]
        if played_current != played_backup:
            print "Setting played status : %s - %s" % (item["Id"], item["Name"])

            item_id = item["Id"]
            set_watched(item_id, played_backup, config, user_info)

    else:
        print "NO matched in backup: %s" % item["Name"]

    percent_done = int((count / float(total)) * 100)
    percent_disp = percent_done % 5 == 0
    count += 1

    if percent_disp and last_percentage != percent_done:
        last_percentage = percent_done
        print "Processed : %s" % percent_done

