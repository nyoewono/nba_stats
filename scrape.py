#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 21:18:18 2021

@author: nathanaelyoewono

All star NBA based on stats
"""

# web scraping tools
from selenium import webdriver
import time

# operating system
import os

# date manipulations
import numpy as np
import pandas as pd
from datetime import date


class GetNBA:
    
    """
    This class was made to scrape NBA player's data from ESPN
    Choose season:
        - Latest: 2021
    """
    
    path = os.getcwd()+'/chromedriver'
    
    def __init__(self, season):
        self.season = season
    
    def _open_browser(self):
        """Open up the browser and set yahoo finance as the default url"""
        # set the chrome optionse
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito") 
    
        # open browser
        self.browser = webdriver.Chrome(executable_path = GetNBA.path, options = chrome_options)
        
        # alternative url
        url = f'https://www.espn.com/nba/stats/player/_/season/{self.season}/seasontype/2/table/offensive/sort/avgPoints/dir/desc'
        
        self.browser.get(url)
    
    def _expand_players(self):
        """Expand the table in espn website"""
        while True:
            try:
                self.browser.find_element_by_xpath('//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[3]/div[2]/a').click()
                time.sleep(1)
            except:
                break
    
    def _get_players(self):
        """Get each player's data"""
        position = ['PG', 'SG', 'C', 'PF', 'SF', 'F']
        self.players = self.browser.find_element_by_xpath('//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[3]/div[1]/div[2]/table').text.split('\n')
        self.stats = self.browser.find_element_by_xpath('//*[@id="fittPageContainer"]/div[3]/div/div/section/div/div[3]/div[1]/div[2]/div/div[2]/table').text.split('\n')

        self.players = [i for i in self.players if i.isnumeric()==False][2:]
        self._extract_pos(self.stats)
        self.stats = [i for i in self.stats if i not in position]
        
        col_name = self.stats[2].split(' ')
        col_name.insert(0, 'GP')
        self.stats = [i.split(' ') for i in self.stats][3:]
                
        self.df = pd.DataFrame(self.stats)
        self.df.columns = col_name
        self.df.dropna(inplace = True)
        self.df['PN'] = self.players
        self.df['POS'] = self.players_position[1:]
        self.df['DATE'] = date.today()
    
    def _extract_pos(self, stats):
        """Extract each player's position"""
        self.players_position = []
        for i in range(len(stats)):
            if i%2!=0:
                self.players_position.append(stats[i])
    
    def _get_injuries(self):
        """Get the injured player's data"""
        
        self.names = []
        self.pos = []
        self.date = []
        self.status = []
        self.comment = []
        
        self.browser.get('https://www.espn.com/nba/injuries')
        time.sleep(2)
        
        counter_div = 2
        
        flag_top = True
        
        while flag_top:
            try:
                counter_rows = 1
                flag_bot = True
                
                while flag_bot:
                    try:
                        self.names.append(self.browser.find_element_by_xpath(f'//*[@id="fittPageContainer"]/div[3]/div/div/section/div/section/div[{counter_div}]/div[2]/div/div[2]/table/tbody/tr[{counter_rows}]/td[1]').text)
                        self.pos.append(self.browser.find_element_by_xpath(f'//*[@id="fittPageContainer"]/div[3]/div/div/section/div/section/div[{counter_div}]/div[2]/div/div[2]/table/tbody/tr[{counter_rows}]/td[2]').text)
                        self.date.append(self.browser.find_element_by_xpath(f'//*[@id="fittPageContainer"]/div[3]/div/div/section/div/section/div[{counter_div}]/div[2]/div/div[2]/table/tbody/tr[{counter_rows}]/td[3]').text)
                        self.status.append(self.browser.find_element_by_xpath(f'//*[@id="fittPageContainer"]/div[3]/div/div/section/div/section/div[{counter_div}]/div[2]/div/div[2]/table/tbody/tr[{counter_rows}]/td[4]').text)
                        self.comment.append(self.browser.find_element_by_xpath(f'//*[@id="fittPageContainer"]/div[3]/div/div/section/div/section/div[{counter_div}]/div[2]/div/div[2]/table/tbody/tr[{counter_rows}]/td[5]').text)
                        counter_rows += 1
                    except:
                        counter_div += 1
                        flag_bot = False
                        if counter_rows==1:
                            flag_top = False
                    
            except:
                flag_top = False
        
        # save the injuries data into a dataframe
        self.injuries = pd.DataFrame([])
        self.injuries['NAMES'] = self.names
        self.injuries['POS'] = self.pos
        self.injuries['DATE'] = self.date
        self.injuries['STATS'] = self.status
        self.injuries['COMMENT'] = self.comment
        
    def run_scrape(self):
        """Run scraping the data"""
        self._open_browser()
        self._expand_players()
        self._get_players()
        self._get_injuries()
        self.browser.close()
    
    def new_df(self):
        """Run this if and only if you don't have the csv files yet"""
        try:
            self.df.to_csv(os.getcwd()+f'/nba_stats_{self.season}.csv', index = False)
            self.injuries.to_csv(os.getcwd()+'/injuries.csv', index = False)
        except:
            print('Do run_scrape first')
            
    def update_df(self):
        """Run this to update the csv files every night"""
        
        # run scraping
        self.run_scrape()
        
        # concatenate stats data
        old_df = pd.read_csv(f'/nba_stats_{self.season}.csv')
        concat_df = [old_df, self.df]
        result = pd.concat(concat_df)
        result.drop_duplicates(subset=['PN'], keep='last', inplace = True)
        result.to_csv(os.getcwd()+f'/nba_stats_{self.season}.csv', index = False)
        
        # concatenate 
        old_injury = pd.read_csv('injuries.csv')
        concat_inj = [old_injury, self.injuries]
        result_inj = pd.concat(concat_inj)
        result_inj.drop_duplicates(subset=['NAMES'], keep='last', inplace = True)
        result_inj.to_csv(os.getcwd()+'/injuries.csv', index = False)
        

#nba = GetNBA()
#nba.run_scrape()
#nba.new_df()
#nba.update_df()
