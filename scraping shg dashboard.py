# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 12:30:23 2023

@author: Sattva Vasavada
"""

import os
import pandas as pd
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait       
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import numpy as np
from collections import Counter

#%%%

url = 'https://nrlm.gov.in/shgOuterReports.do?methodName=showShgreport'

options = webdriver.ChromeOptions()
# options.headless = True #Dont put headless on for some time. Once code is sorted, then do headless. 
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
# options.add_argument("start-maximized")

driver = webdriver.Chrome(ChromeDriverManager(version='114.0.5735.90').install(), 
options=options)

#%%% Defining functions:
    
def click_xpath(xpath, sleep_time):
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                xpath))).click()
    except:
        time.sleep(sleep_time)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                xpath))).click()
        
def send_keys_xpath(xpath, sleep_time, key):
    try:
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                                                    xpath))).send_keys(key)
    except:
        time.sleep(sleep_time)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                                                    xpath))).send_keys(key)
          
        
#%%% Scrape:
  
# df_list = list()

#%%%

driver.get(url)

state_options = len(driver.find_elements_by_xpath('//*[@id="mainex"]/tbody/tr'))

ignore_stateoptions_list = [18, 19, 25, 26, 34, 35, 42, 43]

count = 0

state_stopped = 5
for state_num in list(range(state_stopped , state_options + 1, 1)):
     
    if state_num in ignore_stateoptions_list:
        continue 
    
    #state name:
    statename = (driver.find_element_by_xpath('//*[@id="mainex"]/tbody/tr[' + str(state_num) + ']/td[2]/a')).text.lower()
 
    #select state
    click_xpath('//*[@id="mainex"]/tbody/tr[' + str(state_num) + ']/td[2]/a', 5)

    #needs to be done before getting number of districts. 
    
    #click on view 100 dropdown for districts. 
    click_xpath('//*[@id="example_length"]/label/select', 5)
    
    #click on view 100 for districts: UP has max 75 districts, so we need 100. 
    click_xpath('//*[@id="example_length"]/label/select/option[4]', 5)

    #get number of districts. 
    dist_options = len(driver.find_elements_by_xpath('//*[@id="example"]/tbody/tr'))
    
    for dist_num in list(range(1, dist_options + 1, 1)):

        #click on view 100 dropdown for districts. 
        click_xpath('//*[@id="example_length"]/label/select', 5)

        #click on view 100 for districts: UP has max 75 districts, so we need 100. 
        click_xpath('//*[@id="example_length"]/label/select/option[4]', 5)
                  
        #dist name:
        distname = driver.find_element_by_xpath('//*[@id="example"]/tbody/tr[' + str(dist_num)  + ']/td[2]/a').text.lower()
                
        #click district
        click_xpath('//*[@id="example"]/tbody/tr[' + str(dist_num)  + ']/td[2]/a', 5)

        #now we enter a block
        
        #click on view 100 dropdown for blocks. 
        click_xpath('//*[@id="example_length"]/label/select', 5)
        
        #click on view 100: Max number of blocks cannot be more than 100 (avg 10 blocks per dist). 
        click_xpath('//*[@id="example_length"]/label/select/option[4]', 5)       

        df = (pd.read_html(driver.page_source))

        #get the biggest table. 
        df_len_list = [len(df_len) for df_len in df]

        bigger_table_index = df_len_list.index(np.max(df_len_list))
        df = df[bigger_table_index]
               
        #add statename and distname
        df['statename'] = statename
        df['districtname'] = distname

        df_list.append(df)

        count += 1
        print(count)
        
        #press back button to go to district table 
        click_xpath('//*[@id="panelfilter"]/ul/li/div/input[1]', 5)
        
    #once all distrits are over, go back to main state page. 
    click_xpath('//*[@id="panelfilter"]/ul/li/div/input[1]', 5)
        
    print("State Num: " + str(state_num) + " over.")

#remember to check each table - if it has the rows we want. But this is after scraping.

#%%%
final_df = pd.DataFrame()
count = 0
dfs_not_appended = list()
for df in df_list:
    count += 1
    
    df.columns = ['sr. no', 'blockname', 'shgtype_new', 'shgtype_revived',
                  'shgtype_preNRLM', 'total_shgs', 'total_member', 'statename',
                  'districtname']
    
    df = df.iloc[3: , :]
    
    try:   
        #remove total values. 
        df[df['blockname'] != "Total"]
        
        #convert names to lower
        df['blockname'] = df['blockname'].str.lower()
        
        final_df = pd.concat([df, final_df])
        
    except: 
        dfs_not_appended.append(count)
        
final_df = final_df[final_df['blockname'] != "Total"]

final_df.drop_duplicates(subset = ['statename', 'districtname', 
                                   'blockname', 'total_shgs'], inplace = True)

#save:
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Latest Data Files")
final_df.to_csv("shgdata.csv", index = False)

#%%%

#checkig with distlgd. 
#maha has 34 districts on the website, while LGD has 36. 
#nagaland has 11 districts on the website, while LGD has 16. 
#puduchurry: 2 dist on website, LGD has 4. 
#tamil nadu: 37 on website, 38 on LGD
#telegana: 32 on website, 33 on LGD. 

#Rest all states have the correct district counts. 