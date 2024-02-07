
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
import time
from extract_details import extract_rating_details, get_imdb_rating_url
from store_details import check_exists, load_imdb_ids, sqlite_create_store_table, sqlite_save_details, sqlite_store_stats, sqlite_clean_store_table
#warnings.filterwarnings("ignore")


#store_path = "C:\\Temp\\selenium_test\\store\\"
#if not os.path.exists(store_path):
#    os.makedirs(store_path)

sqlite_store = "imdb_ratings.db"
sqlite_create_store_table(sqlite_store)
sqlite_store_stats(sqlite_store)
time.sleep(5)

opts = Options()
opts.set_preference("permissions.default.stylesheet", 2)
opts.set_preference("permissions.default.image", 2)
opts.add_argument("-headless")
firefox_driver = webdriver.Firefox(options=opts)

imdb_ids = load_imdb_ids("imdb_ids.csv")
#imdb_ids = imdb_ids[:7]
total_ids = len(imdb_ids)
print("Loaded Imdb IDs (%s)" % (total_ids))

# clean store table of no longer needed entries
removed = 0#sqlite_clean_store_table(sqlite_store, imdb_ids)

failed_count = 0
total_processed = 0
total_skipped = 0
max_process = 500
rate_limit = 6 # limit to a request every X sec

for index, imdb_id_item in enumerate(imdb_ids):
    imdb_id = imdb_id_item
    item_prem_date = imdb_ids[imdb_id_item]
    print(f"Processing (%s/%s): %s - %s" % (index+1, total_ids, imdb_id, item_prem_date))
    if not check_exists(imdb_id, item_prem_date, sqlite_store):
        url = get_imdb_rating_url(imdb_id)

        try:
            rating_details = extract_rating_details(firefox_driver, url, rate_limit)
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

        rating_details["imdb_id"] = imdb_id
        print(f"\tSaving : %s (%s)" % (imdb_id, rating_details["title"]))
        #save_details(rating_details, store_path)
        sqlite_save_details(sqlite_store, rating_details)
        #print(rating_details)
        if max_process > 0 and total_processed >= max_process:
            print(f"Reached max process limit, exiting")
            break
    else:
        total_skipped += 1
        print(f"\tSkipping : %s" % (imdb_id))

firefox_driver.quit()

print(f"Total Processed : {total_processed}")
print(f"Total Skipped   : {total_skipped}")
print(f"Total Errors    : {failed_count}")
print(f"Removed {removed} unused entries from store")

sqlite_store_stats(sqlite_store)
