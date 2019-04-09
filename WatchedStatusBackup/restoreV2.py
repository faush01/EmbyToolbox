
import sys
import json
from emby_client import authenticate, get_ulr_data, set_watched


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

# build backup data DB

backup_map = {}
for item in backup_items:
    if item["Type"] == "Movie":
        key_string = item["Name"] + "-" + str(item["Year"])
    elif item["Type"] == "Episode":
        key_string = item["SeriesName"] + "-" + str(item["SeasonNumber"]) + "-" + str(item["EpisodeNumber"])
    backup_map[key_string] = item["Played"]

# check all the items from Emby against the backup Play status

found = 0
not_found = 0
updated = 0

for item in item_list:

    item_match = None
    if item["Type"] == "Movie":
        key_string = item["Name"] + "-" + str(item.get("ProductionYear"))
    elif item["Type"] == "Episode":
        key_string = item["SeriesName"] + "-" + str(item["ParentIndexNumber"]) + "-" + str(item["IndexNumber"])
    item_match = backup_map.get(key_string)

    if item_match is not None:
        found += 1
        played_current = item["UserData"]["Played"]
        if played_current != item_match:
            updated += 1
            print "Setting played status : %s - %s" % (item["Id"], item["Name"])

            item_id = item["Id"]
            set_watched(item_id, item_match, config, user_info)

    else:
        not_found += 1
        item_details = item["Id"] + " - " + item["Type"]
        if item["Type"] == "Episode":
            item_details += " - " + item["SeriesName"] + " - " + str(item["ParentIndexNumber"]) + "x" + str(item["IndexNumber"])
        item_details += " - " + item["Name"]
        print "NO matched for item : %s" % item_details


print "Total Emby Items   : %s" % len(item_list)
print "Total Backup Items : %s" % len(backup_items)
print "Found In Backup    : %s" % found
print "Not Found          : %s" % not_found
print "Updated            : %s" % updated
