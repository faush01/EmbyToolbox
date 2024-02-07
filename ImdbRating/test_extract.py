import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from extract_details import extract_rating_details


opts = Options()
opts.set_preference('permissions.default.stylesheet', 2)
opts.set_preference('permissions.default.image', 2)
opts.add_argument("-headless")
firefox_driver = webdriver.Firefox(options=opts)

url = "https://www.imdb.com/title/tt0111161/ratings"
details = extract_rating_details(firefox_driver, url, 0)

print(details)

firefox_driver.quit()
