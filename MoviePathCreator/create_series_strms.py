import requests
import os

# this is the list of series ids from the movie database site
series_ids = ["60625", "1416", "94605", "71712", "205715", "46952", "1399", "63174", "37680", "211684", "95057",
              "2734", "1434", "1413", "5920", "1419", "44217", "1402", "114461", "79744", "76479", "81356"]

output_path = "C:\\Data\\media\\media_files\\TvShows\\"
strm_item = "C:\\Data\\media\\Arcane-S01-E01.mkv"

tmdb_key = "<api key here>"
tmdb_series_url = "https://api.themoviedb.org/3/tv/%s?api_key=%s"


def clean_series_name(series_name):
    series_name = series_name.replace("'", "")
    series_name = series_name.replace(":", "-")
    return series_name


def process_season(season_path, season_no, episode_count):
    for e_no in range(1, episode_count+1):
        file_name = ("S%02dE%02d.strm" % (season_no, e_no))
        episode_path = os.path.join(season_path, file_name)
        #print(episode_path)
        with open(episode_path, "w", encoding="utf-8") as strm_file:
            strm_file.write(strm_item)


def process_series(series):
    series_name = series_json_data["name"]
    series_first_air = series["first_air_date"]
    series_name = clean_series_name(series_name)
    #print(series_name)
    if series_first_air is not None and len(series_first_air) > 4:
        series_name = series_name + " (" + series_first_air[0:4] + ")"
    print(series_name)
    series_path = os.path.join(output_path, series_name)
    os.makedirs(series_path, exist_ok=True)

    seasons = series_json_data["seasons"]
    for season in seasons:
        if season["season_number"] > 0 and season["episode_count"] > 0:
            #print(season["name"] + " - " + str(season["episode_count"]))
            season_path = "Season %02d" % season["season_number"]
            season_path = os.path.join(series_path, season_path)
            #print (season_path)
            os.makedirs(season_path, exist_ok=True)
            process_season(season_path, season["season_number"], season["episode_count"])
    

for series_id in series_ids:
    show_url = (tmdb_series_url % (series_id, tmdb_key))
    print (show_url)

    resp = requests.get(show_url)
    series_json_data = resp.json()
    process_series(series_json_data)


