
import hashlib
import urllib
import requests


def check_server(config): 
    url = config["emby_server"] + "/emby/System/Info?api_key=" + config["api_key"]
    response = requests.get(url)
    if response.status_code == 200:
        resp = response.json()
        #print(resp)
        print("ServerName : %s" % resp["ServerName"])
        print("Version    : %s" % resp["Version"])
        print("Id         : %s" % resp["Id"])
        return True  
    else:
        print("Response Code : %s" % response.status_code)
        print(response.text)
        return False


def get_user_list(config):

    url = config["emby_server"] + "/emby/users/query?api_key=" + config["api_key"]
    response = requests.get(url)
    resp = response.json()
    #print(resp)
    users = resp["Items"]
    user_list = []
    for user in users:
        #print ("%s : %s" % (user["Name"], user["Id"]))
        user_list.append({"Id": user["Id"], "Name": user["Name"].lower()})
    #print(user_list)
    return user_list


def get_watched_items(config, user_id):
    url = (config["emby_server"] +
            "/emby/Users/" + user_id + "/Items" +
            "?Recursive=true" +
            "&Fields=ProductionYear" +
            "&IsMissing=False"
            "&IncludeItemTypes=Movie,Episode" +
            "&ImageTypeLimit=0" +
            "&api_key=" + config["api_key"])
    
    response = requests.get(url)
    resp = response.json()
    #print(resp)
    watched_item_set = set()
    for item in resp["Items"]:
        if item.get("UserData", {}).get("Played", False) == True:
            key = None
            if item["Type"] == "Movie":
                key = "movie|" + item["Name"].lower() + "|" + str(item["ProductionYear"])
            elif item["Type"] == "Episode":
                key = "episode|" + item["SeriesName"].lower() + "|" + str(item["ProductionYear"]) + "|" + str(item["ParentIndexNumber"]) + "|" + str(item["IndexNumber"])
            watched_item_set.add(key)

    #print(len(watched_item_set))
    return sorted(watched_item_set)


def get_user_items(config, user_id):
    url = (config["emby_server"] +
            "/emby/Users/" + user_id + "/Items" +
            "?Recursive=true" +
            "&Fields=ProductionYear" +
            "&IsMissing=False"
            "&IncludeItemTypes=Movie,Episode" +
            "&ImageTypeLimit=0" +
            "&api_key=" + config["api_key"])

    response = requests.get(url)
    resp = response.json()
    user_item = {}
    for item in resp["Items"]:
        key = None
        if item["Type"] == "Movie":
            key = "movie|" + item["Name"].lower() + "|" + str(item["ProductionYear"])
        elif item["Type"] == "Episode":
            key = "episode|" + item["SeriesName"].lower() + "|" + str(item["ProductionYear"]) + "|" + str(item["ParentIndexNumber"]) + "|" + str(item["IndexNumber"])
        user_item[key] = item["Id"]    

    return user_item

def set_watched(config, user_id, item_id):

    url = (config["emby_server"] +
           "/emby/Users/" + user_id +
           "/PlayedItems/" + item_id +
           "?api_key=" + config["api_key"]
           )

    #print("Setting watched : %s" % url)
    requests.post(url)
    #requests.delete(url)
