import sys
import io
import os
import json
import requests


def get_tv_shows():

    base_output_path = "C:\\Temp\\media-test\\series\\"

    base_url = "https://api.themoviedb.org/3/tv/popular?api_key=aec32a8cca2a15594616bd31d264fbdb&page=%s"

    url = base_url % 1
    print url
    r = requests.get(url)
    results = r.json()
    tv_shows = results.get("results")
    print tv_shows

    for show in tv_shows:
        show_name = show.get("name")
        show_name = show_name.replace(":", "-")
        show_name = show_name.replace("*", "-")

        show_path = base_output_path + "\\" + show_name
        if not os.path.exists(show_path):
            os.makedirs(show_path)

            id = show.get("id")

            show_url = "https://api.themoviedb.org/3/tv/%s?api_key=aec32a8cca2a15594616bd31d264fbdb" % id
            print show_url
            tv_show_info_responce = requests.get(show_url)
            tv_show_info = tv_show_info_responce.json()
            print tv_show_info
            seasons = tv_show_info.get("seasons")

            show_path = base_output_path + "\\" + show_name
            if not os.path.exists(show_path):
                os.makedirs(show_path)

            for season in seasons:
                epp_count = season.get("episode_count")
                season_name = season.get("name")
                season_num = int(season.get("season_number"))
                season_path = show_path + "\\" + season_name
                if not os.path.exists(season_path):
                    os.makedirs(season_path)

                for epp_num in range(1, int(epp_count)):
                    epp_path = season_path + ("\\s%02de%02d.mkv" % (season_num, epp_num))
                    f = open(epp_path, "w+")
                    f.write("This is a test")
                    f.close()

def get_movies():

    base_url = "https://api.themoviedb.org/3/discover/movie?api_key=aec32a8cca2a15594616bd31d264fbdb&sort_by=popularity.desc&page=%s"

    base_output_path = "C:\\Temp\\media-test\\movies\\"

    for x in range(1, 10):
        url = base_url % x
        print url
        r = requests.get(url)
        results = r.json()
        movies = results.get("results")

        for movie in movies:
            title = movie.get("title")
            title = title.replace(":", "-")
            title = title.replace("*", "-")
            year = movie.get("release_date")
            year = year[0:4]
            movie_file_name = "%s (%s)" % (title, year)
            print movie_file_name

            file_name = base_output_path + movie_file_name + ".mkv"
            f = open(file_name, "w+")
            f.write("This is a test")
            f.close()

            '''
            dir_name = base_output_path + movie_file_name
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                file_name = base_output_path + movie_file_name + "\\movie.mkv"
                f = open(file_name,"w+")
                f.write("This is a test")
                f.close()
            '''



get_tv_shows()
