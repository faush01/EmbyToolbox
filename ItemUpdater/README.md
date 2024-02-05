## Item Updater

Emby plugin to facilitate updates to a single Emby library item.  
The plugin creates a new API endpoint (Admin Only) that can be used to update items details.  
Currently, only supports CommunityRating  

### API Example:  

Python:  

```
import requests

url = "http://localhost:8096/emby/item_updater/update?api_key=<emby api key>"

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

result = requests.post(url, json=update_data)
print(result.status_code)
print(result.text)

```
