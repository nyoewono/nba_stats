# nba_stats
A web scraper bot that scrape NBA player stats data

# Source
The data was taken from ESPN. The bot will take each player stats and injury. Ideally, the data should be updated every night, as ESPN update their data every night. 

# Important Functions
- run_scrape: Use this to run the webscraping program, but the data will not be automatically saved in csv format
- new_df: get directly new csv file for both stats and injury
- update_df: get the udpated version of the csv file 

# Season
- Please do specify the season for extra argument when creating the GetNBA class. Ex: 2020-2021 season = 2021
