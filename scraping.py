import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# url = "https://fbref.com/en/comps/12/La-Liga-Stats"

# data = requests.get(url) # saving html page

# soup = BeautifulSoup(data.text) # parsing html content to extract data later

# standings_table = soup.select('table.stats_table')[0] # selecting first element with class stats_table

# links = standings_table.find_all('a') # finding all link elements

# links = [l.get("href") for l in links] # getting href value from each link 
 
# links = [l for l in links if '/squads/' in l] # getting only links which have 'squads' in it

# team_urls = [f"https://fbref.com{l}" for l in links] # getting full team urls

# team_url = team_urls[0] # getting first team url


# data = requests.get(team_url)

# # matches dataframe
# matches = pd.read_html(data.text, match="Scores & Fixtures") # returning table wich has string 'scores & fixtures' inside it


# soup = BeautifulSoup(data.text)

# links = soup.find_all('a')

# links = [l.get("href") for l in links]

# links = [l for l in links if l and 'all_comps/shooting/' in l] # finding shooting link


# data = requests.get(f"https://fbref.com{links[0]}") # selecting first match

# # shootings dataframe
# shootings = pd.read_html(data.text,match="Shooting")[0] # making it into dataframe

# shootings.columns = shootings.columns.droplevel() # removing first column, because don't want multi-level index

# team_data = matches[0].merge(shootings[["Date","Sh", "SoT", "Dist", "FK","PK", "PKatt"]], on="Date") # combining matches and shooting datas based on the Date column

years = list(range(2025,2023, -1)) 

all_matches = []

standings_url = "https://fbref.com/en/comps/12/La-Liga-Stats"


for year in years:
    # getting team urls from standings table
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]
    
    links = [l.get("href") for l in standings_table.find_all('a')] 
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}" # changing url to previous season so each time we loop we get different season

    # looping through each team url
    for team_url in team_urls:
        # extracting club name from url
        team_name = team_url.split("/")[-1].replace("-Stats","").replace("-"," ")
        
        # getting single season stats and combining matches and shooting stats
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]

        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l  in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l] 
        data = requests.get(f"https://fbref.com{links[0]}") 
        shootings = pd.read_html(data.text, match="Shooting")[0]
        shootings.columns = shootings.columns.droplevel()

        try:
            team_data = matches.merge(shootings[["Date","Sh", "SoT", "Dist", "FK","PK", "PKatt"]], on="Date") 
        except ValueError: 
            continue # if shooting stats dont exist skip over team

        team_data = team_data[team_data["Comp"] == "La Liga"] # filtering out games that happened outside of la liga
        team_data["Season"] = year # adding column to know season
        team_data["Team"] = team_name # adding column to know team name

        all_matches.append(team_data)
        time.sleep(5) # sleeping so we dont get blocked from site

print(len(all_matches))

match_df = pd.concat(all_matches) # returning single data frame from list of data frames

print(match_df)
match_df.to_csv("matches.csv") # writing our data to csv file