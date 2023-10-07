 # -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 15:27:23 2023

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

url = 'https://rhreporting.nic.in/netiay/DataAnalytics/PhysicalProgressRpt.aspx'

#initialise drivers and all. 
options = webdriver.ChromeOptions()
options.headless = True #Dont put headless on for some time. Once code is sorted, then do headless. 
prefs = {"profile.managed_default_content_settings.images": 2} #stop images from loading. 
options.add_experimental_option("prefs", prefs)
# options.add_argument("start-maximized")
driver = webdriver.Chrome(ChromeDriverManager().install(), options = options) #download driver. 

#%%% Defining functions:
    
def click_xpath(xpath, sleep_time):
    try:
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                                                xpath))).click()
    except:
        time.sleep(sleep_time)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
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
  
#list where all dfs scraped will be appended to. Then convert this list to a final df. 
df_list = list()

#open url. 
driver.get(url)

#get number of options we have for states. 
state_dropdown_options = len(Select(driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlState"]')).options)

#each state is a row. Iteratre thorugh all rows. 
for state_num in list(range(2, state_dropdown_options + 1, 1)):
    
    #click state option dropdown
    click_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlState"]', 5)
    
    #select state
    click_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlState"]/option[' + str(state_num) + ']', 5)

    #state name:
    statename = Select(driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlState"]')).options[state_num - 1].text
    
    #click district dropdown options
    click_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]', 5)

    dist_dropdown_options = len(Select(driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]')).options)

    for dist_num in list(range(2, dist_dropdown_options + 1, 1)):
        
        #click district
        click_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]/option[' + str(dist_num) +']', 5)

        #dist name:
        distname = Select(driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ddlDistrict"]')).options[dist_num - 1].text
        
        #click submit button
        click_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSubmit"]', 5)
        
        df = (pd.read_html(driver.page_source))
        
        #get the biggest table. 
        df_len_list = [len(df_len) for df_len in df]
        bigger_table_index = df_len_list.index(np.max(df_len_list))
        df = df[bigger_table_index]
        
        #remove the first row - it was not needed. 
        df = df.iloc[1:, :]
        
        #add statename and distname
        df['statename'] = statename
        df['districtname'] = distname

        df_list.append(df)
        
    print("State Num: " + str(state_num) + " over.")

#remember to check each table - if it has the rows we want. But this is after scraping.

#%%%
final_df = pd.DataFrame() #final df where all blocks shall be appended. 
count = 0
dfs_not_appended = list() #if any df is not appended, then list it here. 

for df in df_list:
    count += 1
    try:
        #because 1st row are column headers, we have "Assam" in the first row. Change it. 
        df.at[1, 'statename'] = 'statename'
        df.at[1, 'districtname'] = 'districtname'
               
        #drop first row
        df = df.iloc[1: , :]
        
        #remove total values. 
        df[df['Block Name'] != "Total"]
        
        #convert names to lower
        df['statename'] = df['statename'].str.lower()
        df['districtname'] = df['districtname'].str.lower()
        
        final_df = pd.concat([df, final_df])
    except: 
        dfs_not_appended.append(count)
        
final_df = final_df[final_df['Block Name'] != "Total"]
     
#save:
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Latest Data Files")
final_df.to_csv("pmawaas.csv", index = False)

#%%%