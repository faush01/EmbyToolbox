
import hashlib
import urllib
import requests


def authenticate(config):

    url = config.get("emby_server") + "/Users/AuthenticateByName?format=json"

    pwd_sha = hashlib.sha1(config.get("user_password", "")).hexdigest()

    user_name = urllib.quote(config.get("user_name", ""))
    pwd_text = urllib.quote(config.get("user_password", ""))

    message_data = {}
    message_data["username"] = user_name
    message_data["password"] = pwd_sha
    message_data["pw"] = pwd_text

    headers = get_headers()

    print "Auth Url     : %s" % url
    print "Auth Msg     : %s" % message_data
    print "Auth Headers : %s" % headers
    response = requests.post(url, data=message_data, headers=headers)
    print str(response.text)

    return response.json()


def get_headers(user_info=None):

    auth_string = "MediaBrowser Client=\"EmbyBackup\",Device=\"BackupClient\",DeviceId=\"10\",Version=\"1\""

    if user_info:
        auth_string += ",UserId=\"" + user_info["User"]["Id"] + "\""

    headers = {}

    if user_info:
        headers["X-MediaBrowser-Token"] = user_info["AccessToken"]

    headers["Accept-encoding"] = "gzip"
    headers["Accept-Charset"] = "UTF-8,*"

    headers["X-Emby-Authorization"] = auth_string

    return headers


def get_ulr_data(url, config, user_info):

    if url.find("{server}") != -1:
        server = config["emby_server"]
        url = url.replace("{server}", server)

    if url.find("{userid}") != -1:
        user_id = user_info["User"]["Id"]
        url = url.replace("{userid}", user_id)

    headers = get_headers(user_info)

    response = requests.get(url, headers=headers)
    #print response.text
    return response.json()


def set_watched(item_id, watched_status, config, user_info):

    url = "{server}/emby/Users/{userid}/PlayedItems/" + item_id

    if url.find("{server}") != -1:
        server = config["emby_server"]
        url = url.replace("{server}", server)

    if url.find("{userid}") != -1:
        user_id = user_info["User"]["Id"]
        url = url.replace("{userid}", user_id)

    headers = get_headers(user_info)

    if watched_status:
        requests.post(url, headers=headers)
    else:
        requests.delete(url, headers=headers)


def load_emby_data(cursor, config):
    print "loading"

    user_info = authenticate(config)
    # print "AccessToken Token : %s" % user_info["AccessToken"]

    url = ('{server}/emby/Users/{userid}/Items' +
           '?Recursive=true' +
           '&Fields=MediaSources' +
           '&IsMissing=False'
           # '&IncludeItemTypes=Movie,Episode' +
           '&ImageTypeLimit=0')

    response_data = get_ulr_data(url, config, user_info)
    item_list = response_data["Items"]

    # create the table
    cursor.execute("DROP TABLE IF EXISTS data")
    cursor.execute("CREATE TABLE data (" +
                   "Id int, " +
                   "Name text, " +
                   "Type text, " +
                   "Source_Count int, " +
                   "Video_Width int, " +
                   "Video_Height int, " +
                   "Video_Codec text, " +
                   "Audio_Codec text, " +
                   "Container text, " +
                   "Size long" +
                   ")")

    loaded_count = 0
    for item in item_list:
        loaded_count += 1

        id = item["Id"]
        type = item["Type"]
        name = item["Name"]
        video_width = 0
        video_height = 0
        video_codec = ""
        audio_codec = ""
        container = ""
        source_count = 0
        size = 0

        if item["Type"] == "Episode":
            name = item["Name"]

        media_sources = item.get("MediaSources", [])
        source_count = len(media_sources)
        if len(media_sources) > 0:
            media_source = media_sources[0]
            container = media_source["Container"]
            size = media_source["Size"]

            media_streams = media_source.get("MediaStreams", [])
            for stream in media_streams:
                if stream["Type"] == "Video":
                    video_width = stream["Width"]
                    video_height = stream["Height"]
                    video_codec = stream["Codec"]
                if stream["Type"] == "Audio":
                    audio_codec = stream["Codec"]

        insert_data = (id, name, type, source_count, video_width, video_height, video_codec, audio_codec, container, size)
        cursor.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", insert_data)

    return loaded_count
