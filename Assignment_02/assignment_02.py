
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup

driver = webdriver.Chrome(executable_path='chromedriver')


from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import pandas as pd
from pandas import DataFrame

import random
import time


driver.get('http://www.mlb.com')

wait = WebDriverWait(driver, 10)

stats_header_bar = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'megamenu-navbar-overflow__menu-item--stats')))

normal_delay = random.normalvariate(2, 0.5)
print('Sleeping for {} seconds'.format(normal_delay))
time.sleep(normal_delay)
print('Now moving mouse...')
ActionChains(driver).move_to_element(stats_header_bar).perform()

stats_line_items = stats_header_bar.find_elements_by_tag_name('li')
[li.text for li in stats_line_items]
def select_element_by_text(elements, text):
    for e in elements:
        if e.text == text:
            return e
        
    return None

reg_season_stats_2017 = select_element_by_text(stats_line_items, '2017 Regular Season Stats')

ActionChains(driver).move_to_element(reg_season_stats_2017).click().perform()

def delay(duration):
    normal_delay = max(0,min(duration+1,random.normalvariate(duration, 0.5)))
    time.sleep(normal_delay)

def select_year(year):
    player_stats()
    year_drop_down = driver.find_element_by_xpath('//select[contains(@id,"hitting_season")]')
    delay(2)
    seasons = Select(year_drop_down)
    seasons.select_by_value(year)

def team_stats():
    team_bar = driver.find_element_by_id('st_parent')
    team_bar.click()
    delay(2.5)

def player_stats():
    player_bar = driver.find_element_by_id('sp_parent')
    player_bar.click()
    delay(2.5)

def set_season(season):
    player_stats()
    type_drop_down = driver.find_element_by_xpath('//select[contains(@id,"hitting_game_type")]')
    delay(1.5)
    game_type = Select(type_drop_down)
    game_type.select_by_visible_text(season)

def set_split(group,option):
    player_stats()
    split_drop_down = driver.find_element_by_xpath('//select[contains(@id,"hitting_hitting_splits")]')
    delay(2.5)
    target = split_drop_down.find_element_by_xpath('//optgroup[@label="{}"]/option[text()="{}"]'.format(group,option))
    target.click()

def recover_split():
    player_stats()
    split_drop_down = driver.find_element_by_id('sp_hitting_hitting_splits')
    delay(2.5)
    recover = Select(split_drop_down)
    recover.select_by_value('')

def set_league(league):
    player_stats()
    if league == 'MLB':
        button = driver.find_element_by_xpath('//*[@id="sp_hitting-1"]/fieldset[1]/label[1]')
    elif league == 'AL':
        button = driver.find_element_by_xpath('//*[@id="sp_hitting-1"]/fieldset[1]/label[2]')
    elif league == 'NL':
        button = driver.find_element_by_xpath('//*[@id="sp_hitting-1"]/fieldset[1]/label[3]')
    delay(2)
    button.click()

def set_team(team_name):
    player_stats()
    team_drop_down = driver.find_element_by_xpath('//select[contains(@id,"hitting_team_id")]')
    delay(2.5)
    team_options = Select(team_drop_down)
    team_options.select_by_visible_text(team_name)

def extract_stats_data(driver):
    data_div = driver.find_element_by_id('datagrid')
    data_html = data_div.get_attribute('innerHTML')
    soup = BeautifulSoup(data_html,'html.parser')
    
    def get_colnames(soup):
        df_col_names = []
        for item in soup.find_all('th'):
            df_col_names.append(item['class'][0].split('-')[1])
        return df_col_names
    
    def get_records(soup):
        table_body = soup.find('tbody')
        rows = table_body.find_all('tr')
        row_list = []
        for row in rows:
            row_record = []
            items = row.find_all('td')
            for item in items:
                row_record.append(item.text)
            row_list.append(row_record)
        return row_list
    
    df_col_names = get_colnames(soup)
    records = get_records(soup)
    
    return df_col_names, records

def has_next_page(driver):
    try:
        driver.find_element_by_xpath('//div[@id="pagination" and @style!="display: none;"]')
        driver.find_element_by_xpath('//button[@class="paginationWidget-next" and count(@*)=1]')
        return True
    except:
        return False

def turn_next_page(driver):
    next_button = driver.find_element_by_xpath('//button[@class="paginationWidget-next"]')
    ActionChains(driver).move_to_element(next_button).click().perform()
    delay(4)

def get_data_frame(driver):
    df_col_names, all_records = extract_stats_data(driver)
    try:
        driver.find_element_by_xpath('//button[@class="paginationWidget-last" and text()="1"]')
        df = DataFrame(all_records, columns=df_col_names)
    except:
        while has_next_page(driver):
            _, records = extract_stats_data(driver)
            all_records += records
            turn_next_page(driver)
        df = DataFrame(all_records, columns=df_col_names)
    return df

def get_full_name_by_id(id):
    driver.get('http://m.mlb.com/player/{}'.format(id))
    url = driver.current_url
    player_list = url.split('/')[-1].split('-')
    player_name = ' '.join(player_list)
    delay(0.5)
    return player_name.title()

def get_name_born_location_by_id(player_id):
    driver.get('http://m.mlb.com/player/{}'.format(player_id))
    delay(0.5)
    url = driver.current_url
    player_list = url.split('/')[-1].split('-')
    player_name = ' '.join(player_list)
    born = driver.find_element_by_xpath('//span[text()="Born:"]/parent::li')
    location = born.text.split(' in ')
    return (player_name, location[1])


# In[2]:


# Q_1 GET DATA
select_year('2015')
set_season('Regular Season')
team_stats()

Q1_df = get_data_frame(driver)
Q1_df.to_csv('Question_1.csv',index=False)
Q1_df = pd.read_csv('Question_1.csv')


# In[3]:


# Q_2 get_data
select_year('2015')
set_split('Inning','First Inning')
set_season('Regular Season')
team_stats()

df_Q2_first_inning = get_data_frame(driver)
df_Q2_first_inning.to_csv('Question_2.csv',index=False)
df_Q2_first_inning = pd.read_csv('Question_2.csv')


# In[4]:


# Q_3 get_data
select_year('2017')
recover_split()
set_season('Regular Season')
set_team('New York Yankees')

Q3_df = get_data_frame(driver)
Q3_df.drop_duplicates()

Q3_df.to_csv('Question_3.csv',index=False)
Q3_df = pd.read_csv('Question_3.csv')


# In[5]:


# Q_4 get_data
select_year('2015')
set_team('All Teams')
set_league('AL')
set_season('Regular Season')
recover_split()

Q4_df = get_data_frame(driver)
Q4_df.to_csv('Question_4.csv', index=False)
Q4_df = pd.read_csv('Question_4.csv')


# In[6]:


# Q_5 get_data
select_year('2014')
set_league('MLB')
set_season('All-Star Game')
Q5_df = get_data_frame(driver)
Q5_df.to_csv('Question_5.csv',index_label=False)
Q5_df = pd.read_csv('Question_5.csv')


# In[7]:


import http.client, urllib.request

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': 'a27a8e92364f4356957c1be7b2e355d9',
}

# https://api.fantasydata.net/v3/mlb/stats/JSON/Games/2016
try:
    conn = http.client.HTTPSConnection('api.fantasydata.net')
    conn.request("GET", "/v3/mlb/stats/JSON/Games/{}".format(2016), "{body}", headers)
    response = conn.getresponse()
    data_schedules = response.read()
    conn.request("GET", "/v3/mlb/stats/json/Stadiums","{body}",headers)
    response = conn.getresponse()
    data_stadiums = response.read()
    conn.request("GET", "/v3/mlb/stats/json/AllTeams","{body}",headers)
    response = conn.getresponse()
    data_teams = response.read()
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))


schedules_df = pd.read_json(data_schedules)
team_df = pd.read_json(data_teams)
stadiums_df = pd.read_json(data_stadiums)

schedules_df.to_json('schedules.json')
team_df.to_json('team.json')
stadiums_df.to_json('stadium.json')


# In[8]:


Q1_df = pd.read_csv('Question_1.csv')
df_Q2_first_inning = pd.read_csv('Question_2.csv')
Q3_df = pd.read_csv('Question_3.csv')
Q4_df = pd.read_csv('Question_4.csv')
Q5_df = pd.read_csv('Question_5.csv')


# In[9]:


#Q1
Q1_df['file_code'] = Q1_df['file_code'].apply(lambda x: x.upper())
hr_most_team = Q1_df.sort_values('hr',ascending=False).iloc[0]['team_full']
print('A1 team {} had the most homeruns in the regular season of 2015'.format(hr_most_team))

#Q2
higher_league = Q1_df[['league','hr']].groupby('league').mean().index[0]
score = Q1_df[['league','hr']].groupby('league').mean().hr[0]
print('A2 a) the {} league had the greatest number of homeruns in 2015 regular season, wich is {}'.format(higher_league, score))

higher_league_Q2 = df_Q2_first_inning[['league','hr']].groupby('league').mean().index[0]
score_Q2 = df_Q2_first_inning[['league','hr']].groupby('league').mean().hr[0]
print('A2 b) In first Inning, the {} league had the greatest number of homeruns in 2015 first inning, wich is {}'.format(higher_league_Q2, score_Q2))


# In[11]:


Q3_a = Q3_df[Q3_df['ab']>=30]
Q3_a_player = Q3_a.sort_values('avg',ascending=False).iloc[0]
Q3_a_name = get_full_name_by_id(Q3_a_player['player_id'])
print('Q3 a) {} played in 2017 regular season with at least 30 bats, and he had the best overall batting average'.format(Q3_a_name))

Q3_b = Q3_df[Q3_df['pos'].isin(['LF', 'CF','RF'])]
Q3_b_player = Q3_b.sort_values('avg',ascending=False).iloc[0]
Q3_b_name = get_full_name_by_id(Q3_b_player['player_id'])
Q3_b_pos = Q3_b_player['pos']
print('Q3 b) {} played in the outfield of {}, and he had the best overall batting average in 2017'.format(Q3_b_name,Q3_b_pos))


# In[12]:


Q1_df['file_code'] = Q1_df['file_code'].apply(lambda x: x.upper())
Q4_df=pd.merge(Q1_df[['team_full','file_code']],Q4_df,left_on='file_code',right_on='team_abbrev')
Q4_person = Q4_df.sort_values('ab',ascending=False).iloc[0]
Q4_name = get_full_name_by_id(Q4_person['player_id'])
Q4_team = Q4_person['team_full']
Q4_pos = Q4_person['pos']

print('Q4 {} played for team {} in the position of {}, and he had the best overall batting average in 2015 regular season'.format(Q4_name,Q4_team,Q4_pos))


# In[ ]:


#Q5
Q5_df['name_born'] = Q5_df['player_id'].apply(get_name_born_location_by_id)
Q5_df['full_name'] = Q5_df['name_born'].apply(lambda x: x[0])
Q5_df['born_place'] = Q5_df['name_born'].apply(lambda x: x[1])
Latin_america_countries=('Argentina','Bolivia','Brazil','Chile','Colombia','Costa Rica','Cuba','Dominican Republic','Ecuador','EI Salvador','French Guiana','Guadeloupe','Guatemala',
                         'Haiti','Honduras','Martinique','Mexico','Nicaragua','Panama','Paraguay','Peru','Puerto Rico','Saint Barthelemy','Saint Martin','Uruguay','Venezuela')

Q5_df['player_born_country'] = Q5_df['born_place'].apply(lambda x: x.split(', ')[1])
Q5_df = pd.merge(Q5_df, Q1_df[['team_full','file_code']],left_on='team_abbrev',right_on='file_code')
Q5_df[Q5_df['player_born_country'].isin(Latin_america_countries)]

Q5_result = Q5_df[Q5_df['player_born_country'].isin(Latin_america_countries)]
length = Q5_result.shape[0]

for i in range(length):
    player = Q5_result.iloc[i]
    player_name = player['full_name']
    player_team = player['team_full']
    print('Q5 {} was born in latin america, and he played for team {} in 2014 all-star game'.format(player_name, player_team))


# In[13]:


team_df = team_df[['TeamID','City','Name']]
team_df['Full Name'] = team_df['City'] + ' ' + team_df['Name']
Astros_id = team_df[team_df['Full Name'] == 'Houston Astros'].iloc[0]['TeamID']
schedules_df = schedules_df[['GameID','DateTime','AwayTeamID','HomeTeamID','StadiumID']]
stadiums_df = stadiums_df[['StadiumID','Name','City','State']]
schedules_df = schedules_df[(schedules_df['AwayTeamID'] == Astros_id) | (schedules_df['HomeTeamID'] == Astros_id)]

merged_df = pd.merge(schedules_df, team_df, left_on='HomeTeamID', right_on='TeamID')
merged_df = pd.merge(merged_df, team_df, left_on='AwayTeamID', right_on='TeamID')
merged_df = pd.merge(merged_df, stadiums_df, on='StadiumID')

merged_df.drop(['City_x','Name_x','City_y','Name_y'],axis=1,inplace=True)
merged_df['DateTime'] = merged_df['DateTime'].dt.date
record_length = merged_df.shape[0]
for record_index in range(record_length):
    record = merged_df.iloc[record_index]
    game_date = record['DateTime']
    game_stadium = record['Name']
    game_opponent = record['Full Name_x'] if record['Full Name_y'] == 'Houston Astros' else record['Full Name_y']
    game_city = record['City']
    game_state = record['State']
    print('{}   {}   {}   {}   {}'.format(game_opponent, game_date, game_stadium, game_city, game_state))

