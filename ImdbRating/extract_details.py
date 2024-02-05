from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time


def parse_user_rating(data):
    pattern = "([0-9]{1,2}) - ([0-9\.]+)% \(([0-9\.K]+) Ratings\)"
    match = re.search(pattern, data)
    if match:
        rank = match.group(1)
        percent = match.group(2)
        count = match.group(3)
        if rank is None or rank == "": raise Exception("Rank not found")
        if percent is None or percent == "": raise Exception("Percent not found")
        if count is None or count == "": raise Exception("Count not found")
        #print("%s - %s - %s" % (rank, percent, count))
        result = {}
        result["rank"] = rank
        result["percent"] = percent
        result["count"] = count
        return result


def get_imdb_rating_url(imdb_id):
    return f"https://www.imdb.com/title/{imdb_id}/ratings/"


def extract_rating_details(browser_driver, url, rate_limit=0):
    start = time.perf_counter()
    browser_driver.get(url)

    toc = time.perf_counter()
    print(f"\tGet url {toc - start:0.4f} seconds")

    # wait for user rating list svg image to be built
    wait = WebDriverWait(browser_driver, 15)
    wait_event = EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and @aria-label="User ratings chart"]'))
    wait.until(wait_event)

    toc = time.perf_counter()
    print(f"\tWait for page {toc - start:0.4f} seconds")

    rating_details = {}
    #print("Page URL:", browser_driver.current_url) 
    #print("Page Title:", browser_driver.title)

    rating_details["title"] = browser_driver.title
    rating_details["url"] = browser_driver.current_url

    extract_rating(browser_driver, rating_details)
    extract_user_ratings(browser_driver, rating_details)

    toc = time.perf_counter()
    print(f"\tExtract page data {toc - start:0.4f} seconds")    

    rating_details["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

    sleep_for = rate_limit - (toc - start)
    if sleep_for > 0:
        print(f"\tSleeping for {sleep_for:0.4f} seconds")
        time.sleep(sleep_for)

    return rating_details


def extract_rating(browser_driver, rating_details):
    rating_block = browser_driver.find_element(By.XPATH, '//div[@data-testid="ratings-ingress__container"]')
    ratting_span = rating_block.find_element(By.XPATH, "div[1]/div[2]/div[2]/div[1]/span[1]")
    rating_count = rating_block.find_element(By.XPATH, "div[1]/div[2]/div[2]/div[2]")
    if ratting_span.text is None or ratting_span.text == "": raise Exception("Rating not found")
    if rating_count.text is None or rating_count.text == "": raise Exception("Count not found")
    #print("ratting_span: " + ratting_span.text)
    #print("rating_count: " + rating_count.text)
    rating_details["rating"] = ratting_span.text
    rating_details["rating_count"] = rating_count.text


def extract_user_ratings(browser_driver, rating_details):
    item = browser_driver.find_element(By.XPATH, '//*[local-name()="svg" and @aria-label="User ratings chart"]')
    svg_path_items = item.find_elements(By.TAG_NAME, "path")

    user_dattings = []
    for path_item in svg_path_items:
        roll_attrib = path_item.get_attribute("role")
        if roll_attrib == "img":
            ratting_label = path_item.get_attribute("aria-label")
            user_ratting = parse_user_rating(ratting_label)
            user_dattings.append(user_ratting)
            #print("ratting_label: ", ratting_label)
    rating_details["user_ratings"] = user_dattings


def extract_user_ratings_old(browser_driver, rating_details):
    svg_items = browser_driver.find_elements(By.TAG_NAME, "svg") #'aria-label="User ratings chart"')
    for item in svg_items:
        aria_label = None
        try:
            aria_label = item.get_attribute("aria-label")
        except Exception as err:
            pass
        if aria_label == "User ratings chart":
            print("Aria Label:", aria_label)
            svg_path_items = item.find_elements(By.TAG_NAME, "path")
            for path_item in svg_path_items:
                roll_attrib = path_item.get_attribute("role")
                if roll_attrib == "img":
                    ratting_label = path_item.get_attribute("aria-label")
                    print("ratting_label: ", ratting_label)

