import requests
import os
import time


def emby_get_items():

    emby_url = os.environ.get('emby_url')
    api_key = os.environ.get('api_key')
    url = emby_url
    url += "/emby/Items"
    url += "?Recursive=True"
    url += "&IncludeItemTypes=Movie,Episode" # Movie,Episode
    url += "&Fields=ProviderIds,PremiereDate,CommunityRating"
    url += "&SortBy=PremiereDate"
    url += "&SortOrder=Descending"
    url += "&ImageTypeLimit=0"
    url += "&api_key=" + api_key

    print("Emby URL : %s" % url)
    time.sleep(5)

    result = requests.get(url)
    items = result.json()["Items"]

    return items


def emby_update_items(new_ratings):

    emby_url = os.environ.get('emby_url')
    api_key = os.environ.get('api_key')
    url = emby_url + "/emby/item_updater/update?api_key=" + api_key

    '''
    update_data = {
        "UpdateActions": [
            {
                "Id": 4450,
                "Type": "CommunityRating",
                "Value": "3.32"
            },
            {
                "Id": 4449,
                "Type": "CommunityRating",
                "Value": "4.43"
            }
        ]
    }
    '''

    update_data = {
        "UpdateActions": new_ratings
    }

    result = requests.post(url, json=update_data)
    print(result.status_code)
    print(result.text)

