import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://fbref.com/en/comps/12/La-Liga-Stats"

data = requests.get(url) # saving html page

soup = BeautifulSoup(data.text) # parsing html content to extract data later

standings_table = soup.select('table.stats_table')[0] # selecting first element with class stats_table

links = standings_table.find_all('a') # finding all link elements

links = [l.get("href") for l in links] # getting href value from each link 
 
links = [l for l in links if '/squads/' in l] # getting only links which have 'squads' in it

team_urls = [f"https://fbref.com{l}" for l in links] # getting full team urls

team_url = team_urls[0] # getting first team url


data = requests.get(team_url)

# matches dataframe
matches = pd.read_html(data.text, match="Scores & Fixtures") # returning table wich has string 'scores & fixtures' inside it


soup = BeautifulSoup(data.text)

links = soup.find_all('a')

links = [l.get("href") for l in links]

links = [l for l in links if l and 'all_comps/shooting/' in l] # finding shooting link


data = requests.get(f"https://fbref.com{links[0]}") # selecting first match

# shootings dataframe
shootings = pd.read_html(data.text,match="Shooting")[0] # making it into dataframe

shootings.columns = shootings.columns.droplevel() # removing first column, because don't want multi-level index

team_data = matches[0].merge(shootings[["Date","Sh", "SoT", "Dist", "FK","PK", "PKatt"]], on="Date") # combining matches and shooting datas based on the Date column

print(team_data.head())  # returning first 5 elements
