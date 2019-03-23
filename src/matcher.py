
external_names = ["IMDb", "TheMovieDb", "TheTVDB", "Trakt"]

def item_is_match(item, backup_item):

    if item["Type"] == backup_item["Type"]:

        external_urls = item["ExternalUrls"]
        external_urls_backup = backup_item["ExternalUrls"]
        external_match = False
        for external_name in external_names:

            external_url = extract_url(external_urls, external_name)
            external_url_backup = extract_url(external_urls_backup, external_name)
            if external_url is not None and external_url_backup is not None and external_url == external_url_backup:
                external_match = True
                #print "External Url Matched : " + external_name
                break

        if not external_match:
            return False

        if item["Type"] == "Movie":
            if item["Name"] == backup_item["Name"]:
                return True

        elif item["Type"] == "Episode":
            if (item["SeriesName"] == backup_item["SeriesName"] and
                    item["ParentIndexNumber"] == backup_item["SeasonNumber"] and
                    item["IndexNumber"] == backup_item["EpisodeNumber"]):
                return True

    return False

def extract_url(external_urls, name):
    for external_url in external_urls:
        if external_url["Name"] == name:
            return external_url["Url"]
    return None

