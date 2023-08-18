from emby_client import check_server, get_user_list, get_watched_items
import json
import os

overwrite_all = False

with open("config.json", 'r') as f:
    config = json.load(f)

print ("Emby Server           : %s" % config["emby_server"])
print ("ApiKey                : %s" % config["api_key"])
print ("Backup Path           : %s" % config["output_path"])

try:
    os.mkdir(config["output_path"])
except:
    pass

check_server(config)
user_list = get_user_list(config)
print("Backup users:")
for user in user_list: print(" - %s" % user["Name"])
print("To path : %s" % config["output_path"])
ans = input("Are you sure (y,n,all)? ")
if ans.lower() == "all":
    overwrite_all = True
elif ans.lower() != "y":
    exit()

for user in user_list:
    watched_items = get_watched_items(config, user["Id"])
    output_path = os.path.join(config["output_path"], "watched-" + user["Name"] + ".txt")
    print ("Backup File : %s" % output_path)
    if os.path.exists(output_path) and not overwrite_all:
        ans = input("File exists, overwrite (y,n,all)? ")
        if ans.lower() == "all": overwrite_all = True
        if not overwrite_all and ans.lower() != "y":
            print ("Backup skipped")
            continue
    print ("Backup written")
    with open(output_path, 'w') as f:
        for line in watched_items:
            f.write(line + "\n")
