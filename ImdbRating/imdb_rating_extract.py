
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
import time
import sys
from extract_details import extract_rating_details, get_imdb_rating_url
from store_details import check_exists, sqlite_create_store_table, sqlite_save_details, sqlite_store_stats, load_emby_items, sqlite_clean_store_table
#warnings.filterwarnings("ignore")

#sys.stdin.reconfigure(encoding='utf-8')
#sys.stdout.reconfigure(encoding='utf-8')
#sys.stderr.reconfigure(encoding='utf-8')

sqlite_store = "imdb_ratings.db"
sqlite_create_store_table(sqlite_store)
sqlite_store_stats(sqlite_store)

opts = Options()
opts.set_preference("permissions.default.stylesheet", 2)
opts.set_preference("permissions.default.image", 2)
opts.add_argument("-headless")
firefox_driver = webdriver.Firefox(options=opts)

emby_items = load_emby_items("emby_items.tsv")

#emby_items = emby_items[:2]
total_ids = len(emby_items)
print("Loaded Imdb IDs (%s)" % (total_ids))

# clean store table of no longer needed entries
removed = 0#sqlite_clean_store_table(sqlite_store, imdb_ids)

failed_count = 0
total_processed = 0
total_skipped = 0
max_process = 500
rate_limit = 5 # limit to a request every X sec
index = 0

for emby_item in emby_items:
    imdb_id = emby_item["imdb_id"]
    item_prem_date = emby_item["prem_date"]
    index += 1
    print(f"Processing (%s/%s): %s - %s" % (index, total_ids, imdb_id, item_prem_date))
    if not check_exists(imdb_id, item_prem_date, sqlite_store):
        url = get_imdb_rating_url(imdb_id)

        try:
            rating_details, timming_data = extract_rating_details(firefox_driver, url)
            total_processed += 1
        except Exception as e:
            print(f"\tFailed : %s" % (imdb_id))
            print(e)
            rating_details = None
            failed_count += 1
            if failed_count > 20:
                print(f"\tToo many failed attempts, exiting")
                break
            continue

        print("\tGet {0:.3f} Render {1:.3f} Extract {2:.3f}".format(timming_data["get_url"], timming_data["wait_for_page"], timming_data["extract_data"]))

        rating_details["imdb_id"] = imdb_id
        print("\tSaving : %s %s (%s)" % (imdb_id, rating_details["rating"], rating_details["title"]), flush=True)
        #save_details(rating_details, store_path)
        sqlite_save_details(sqlite_store, rating_details)
        #print(rating_details)
        if max_process > 0 and total_processed >= max_process:
            print(f"Reached max process limit, exiting")
            break

        # rate limit requests
        sleep_for = rate_limit - timming_data["extract_data"]
        if sleep_for > 0:
            print(f"\tSleeping for {sleep_for:0.3f} seconds")
            time.sleep(sleep_for)

    else:
        total_skipped += 1
        print(f"\tSkipping : %s" % (imdb_id), flush=True)

firefox_driver.quit()

print(f"Total Processed : {total_processed}")
print(f"Total Skipped   : {total_skipped}")
print(f"Total Errors    : {failed_count}")
print(f"Removed {removed} unused entries from store")

sqlite_store_stats(sqlite_store)
