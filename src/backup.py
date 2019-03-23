

from emby_client import authenticate
from emby_client import get_ulr_data
import json
import os

with open("config.json", 'r') as f:
    config = json.load(f)

print "Emby Server : %s" % config["emby_server"]
print "User Name   : %s" % config["user_name"]
print "User Pass   : %s" % config["user_password"]

try:
    os.mkdir(config["output_path"])
except:
    pass

output_path = os.path.join(config["output_path"], "backup-" + config["user_name"] + ".json")
print "Backup File : %s" % output_path

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
backup_data = {}
backup_data["config"] = config
backup_data["Items"] = []

for item in item_list:
    #print str(item)
    item_data = {}
    item_data["Type"] = item["Type"]
    item_data["Played"] = item["UserData"]["Played"]
    item_data["Name"] = item["Name"]

    if item["Type"] == "Episode":
        item_data["SeriesName"] = item["SeriesName"]
        item_data["SeasonNumber"] = item["ParentIndexNumber"]
        item_data["EpisodeNumber"] = item["IndexNumber"]

    item_data["Path"] = item["Path"]
    item_data["ExternalUrls"] = item["ExternalUrls"]

    backup_data["Items"].append(item_data)

with open(output_path, 'w') as f:
    json.dump(backup_data, f)

print "Backup Saved"
print "Item Count : %s" % len(backup_data["Items"])

