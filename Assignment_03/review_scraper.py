# coding: utf - 8

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import dateparser
import random
import time
import datetime
from pandas import DataFrame

DRIVER_PATH = 'C:/Users/SaulR/Documents/BIA_in_Stevens/Courses/BIA_660/chromedriver_win32/chromedriver.exe'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)


def delay():
    normal_delay = max(3, min(2, random.normalvariate(1.5, 0.5)))
    time.sleep(normal_delay)


def select_verified():
    filter_drop_down = driver.find_element_by_id('reviewer-type-dropdown')
    ActionChains(driver).move_to_element(filter_drop_down).click().perform()
    delay()
    types = Select(filter_drop_down)
    types.select_by_visible_text('Verified purchase only')


def has_next_page(driver):
    try:
        driver.find_element_by_xpath('//li[@class="a-last"]')
        return True
    except:
        return False


def turn_next_page(driver):
    next_button = driver.find_element_by_xpath('//li[@class="a-last"]')
    ActionChains(driver).move_to_element(next_button).click().perform()
    delay()


def get_review_sections(driver):
    review_sections = driver.find_elements_by_xpath('//*[@class="a-section review"]')
    return review_sections


def get_review_data(review):
    review_html = review.get_attribute('innerHTML')
    soup = BeautifulSoup(review_html, 'html.parser')
    review_id = soup.find('div').attrs['id'].split('-')[1]
    review_star = float(soup.find('i').text[:3])
    review_date = soup.find('span',{"data-hook":"review-date"}).text[3:]
    review_date = dateparser.parse(review_date)
    review_body = ''
    if u'\xa0' in soup.find('span',{"data-hook":"review-body"}).text:
        review_body = soup.find('span',{"data-hook":"review-body"}).text.split(u'\xa0')[1]
    else:
        review_body = soup.find('span',{"data-hook":"review-body"}).text
    helpful_vote = 0
    try:
        n = soup.find('span', {"data-hook": "helpful-vote-statement"}).text.strip().split(' ')[0]
        helpful_vote = 1 if n == 'One' else n
    except:
        pass
    with_video = 0 if soup.find('div',{"class":"airy-play-toggle-hint-container airy-scalable-hint-container"}) is None else 1
    with_pic = 0 if soup.find('img',{"alt":"review image"}) is None else 1
    review_dict = {'id':review_id,'star':review_star, 'date':review_date, 'text':review_body, 'hp_vote':helpful_vote, 'with_video':with_video, 'with_pic':with_pic}
    return review_dict


def get_page_reviews(driver):
    records = []
    review_sections = get_review_sections(driver)
    for review in review_sections:
        record = get_review_data(review)
        if record['date'] > dateparser.parse('2017-01-01'):
            records.append(record)
    return records


def get_data_frame(driver):
    all_record = get_page_reviews(driver)
    while has_next_page(driver):
        records = get_page_reviews(driver)
        all_record += records
        turn_next_page(driver)
    df_records = DataFrame(all_record)
    return df_records

starting_page = 'https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM'
driver.get(starting_page)
delay()
select_verified()
delay()

df = get_data_frame(driver)
df.to_json('review_data.json',lines=True,orient='records')
