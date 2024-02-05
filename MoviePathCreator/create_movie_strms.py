import requests
import os

output_path = "C:\\Data\\media\\media_files\\Movies\\"
strm_item = "C:\\Data\\media\\Arcane-S01-E01.mkv"

tmdb_key = "<api key here>"

# https://developer.themoviedb.org/reference/discover-movie
base_url = "https://api.themoviedb.org/3/discover/movie"
base_url += "?language=en"
base_url += "&with_original_language=en"
base_url += "&include_adult=false"
base_url += "&vote_average.gte=6.5"
base_url += "&vote_average.lte=9.5"
#base_url += "&sort_by=vote_average.desc"
base_url += "&release_date.gte=2020-01-01"
base_url += "&vote_count.gte=100"
base_url += "&page=%s"
base_url += "&api_key=" + tmdb_key

pages = 10


def clean_name(value):
    movie_name = value.replace("'", "")
    movie_name = movie_name.replace(":", " ")

    while movie_name.find("  ") > -1:
        movie_name = movie_name.replace("  ", " ")

    return movie_name


def create_strm(movie_name):
    movie_path = os.path.join(output_path, movie_name + ".strm")
    with open(movie_path, "w", encoding="utf-8") as strm_file:
        strm_file.write(strm_item)

    #os.makedirs(movie_path, exist_ok=True)
    #strm_path = os.path.join(movie_path, "movie.strm")
    #with open(strm_path, "w", encoding="utf-8") as strm_file:
    #    strm_file.write(strm_item)


def process_page(page_url):
    print(page_url)
    resp = requests.get(page_url)
    page_data_json = resp.json()
    movie_items = page_data_json["results"]
    for movie in movie_items:
        title = movie["title"]
        title = clean_name(title)
        if len(movie["release_date"]) > 4:
            title += " (" + movie["release_date"][0:4] + ")"
        print(title)
        create_strm(title)


for page_id in range(1, pages+1):
    page_url = base_url % page_id
    process_page(page_url)


