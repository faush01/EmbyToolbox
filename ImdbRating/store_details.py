import json
import sqlite3
from contextlib import closing
from datetime import datetime


def check_exists(imdb_id, item_prem_date, sqlite_store):
    #output_path = base_path + imdb_id + ".json"

    max_update_age = 60*60*24*30 # 30 days
    prem_date_window = 60*60*24*30 # 30 days

    prem_date = datetime.strptime(item_prem_date, "%Y-%m-%d")
    diff = datetime.now() - prem_date
    if diff.total_seconds() < prem_date_window:
        print("\tToo recent, since prem : %s" % (diff))
        return False

    # load from DB if available
    details_info = sqlite_load_rating_details(sqlite_store, imdb_id)
    if details_info is not None:
        updated = details_info.get("updated")
        if updated:
            u_date = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S")
            age = datetime.now() - u_date
            if age.total_seconds() < max_update_age:
                print("\tIn store, age : %s" % (age))
                return True
            else:
                print("\tToo old, age: %s" % (age))
                return False
        else:
            print("\tNo update stamp")
            return False
    else:
        print("\tNot in store")
        return False


def save_details(rating_details, base_path):
    output_path = base_path + rating_details["imdb_id"] + ".json"
    with open(output_path, "w") as file:
        file.write(json.dumps(rating_details, indent=4))


def load_imdb_ids(imdb_file):
    imdb_ids = {}
    with open(imdb_file, "r") as file:
        for line in file:
            line_tokens = line.strip().split(",")
            imdb_ids[line_tokens[0]] = line_tokens[1]
    return imdb_ids


def sqlite_create_store_table(store_file):
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            sql_create = "CREATE TABLE IF NOT EXISTS imdb_ratings ("
            sql_create += "imdb_id TEXT, "
            sql_create += "rating TEXT, "
            sql_create += "PRIMARY KEY (imdb_id)"
            sql_create += ")"
            cursor.execute(sql_create)
            conn.commit()


def sqlite_load_rating_details(store_file, imdb_id):
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT imdb_id, rating FROM imdb_ratings WHERE imdb_id = ?", (imdb_id,))
            row = cursor.fetchone()
            if row is not None:
                details_info = json.loads(row[1])
                return details_info
            else:
                return None


def sqlite_save_details(store_file, rating_details):
    details_json = json.dumps(rating_details)
    imdb_id = rating_details["imdb_id"]
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("REPLACE INTO imdb_ratings (imdb_id, rating) VALUES (?, ?)", (imdb_id, details_json))
            conn.commit()


def sqlite_store_stats(store_file):
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT count(*) FROM imdb_ratings")
            row = cursor.fetchone()
            print("Total Stored : ", row[0])


def sqlite_create_store_table(store_file):
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            sql_create = "CREATE TABLE IF NOT EXISTS imdb_ratings ("
            sql_create += "imdb_id TEXT, "
            sql_create += "rating TEXT, "
            sql_create += "PRIMARY KEY (imdb_id)"
            sql_create += ")"
            cursor.execute(sql_create)
            conn.commit()


def sqlite_clean_store_table(store_file, imdb_ids_list):
    removed = 0
    existing_imdb_ids = []
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute("SELECT imdb_id FROM imdb_ratings")
            row = cursor.fetchone()
            while row is not None:
                existing_imdb_ids.append(row[0])
                row = cursor.fetchone()
    with closing(sqlite3.connect(store_file)) as conn:
        with closing(conn.cursor()) as cursor:
            for imdb_id in existing_imdb_ids:
                if imdb_id not in imdb_ids_list:
                    print("Removing %s from store" % (imdb_id,))
                    removed += 1
                    cursor.execute("DELETE FROM imdb_ratings WHERE imdb_id = ?", (imdb_id,))
            conn.commit()
    return removed

