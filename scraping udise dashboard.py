# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 13:50:55 2023

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

options = webdriver.ChromeOptions()
# options.headless = True #Dont put headless on for some time. Once code is sorted, then do headless. 
prefs = {"download.default_directory": r"D:\Users\savas\Documents\Ashoka\Economics\NITI Aayog\Aspirational Blocks Program\Block Analysis\data\Latest Data Files\Education Files from Internet"}
options.add_experimental_option("prefs", prefs)
# options.add_argument("start-maximized")
driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)

#%%% Defining functions:
    
def click_xpath(xpath, sleep_time):
    try:
        return WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                xpath))).click()
    except:
        time.sleep(sleep_time)
        return WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                xpath))).click()
        
def send_keys_xpath(xpath, sleep_time, key):
    try:
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                                                    xpath))).send_keys(key)
    except:
        time.sleep(sleep_time)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,
                                                                    xpath))).send_keys(key)
          
#%%% 

url= 'https://dashboard.udiseplus.gov.in/#/reportDashboard/sReport'

def scrapevar(driver, varxpath, year):
    
    #open url
    driver.get(url)

    #click on var xapth
    click_xpath(varxpath, 5)
    
    if year == 2021:
        pass
    elif year == 2020:
        #click on year list dropdown
        click_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[1]/div/div/select', 5)
        
        #click on 2020-21 year. 
        click_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[1]/div/div/select/option[2]', 5)
    
    # #click on state dropdown box
    # click_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[2]/div/div/select', 5)
    
    #get number of states
    numstates = len(Select(driver.find_element_by_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[2]/div/div/select')).options)

    #click on state
    for statenum in range(3, numstates + 1, 1):
        #click on state number
        click_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[2]/div/div/select/option['+str(statenum)+']', 5)
    
        # #click on district dropdown
        # click_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[3]/div/div/select', 5)
        
        #click on districtwise report
        click_xpath('/html/body/ngb-modal-window/div/div/div[2]/div[1]/div/div/div[3]/div/div/select/option[2]', 5)
        
        #download xlsx file
        click_xpath('/html/body/ngb-modal-window/div/div/div[1]/div/div[1]/div/div[2]/ul/li[3]/img', 5)
        
#%%% Scrape 

#Total Number of Schools
scrapevar(driver,
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[1]/div/div/div/div/div[2]/table/tr[1]/td[5]/img[2]',
          2021)   

#Enrollment by class, 2021:
scrapevar(driver, 
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[1]/div/div/div/div/div[2]/table/tr[4]/td[5]/img[2]', 
          2021)                      

#Enrollment by class, 2020:
scrapevar(driver, 
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[1]/div/div/div/div/div[2]/table/tr[4]/td[5]/img[2]', 
          2020)  
        
#Pupil Teacher Ratio
scrapevar(driver, 
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[3]/div/div/div/div/div[2]/table/tr[7]/td[5]/img[2]', 
          2021)

#functional girls toilet
scrapevar(driver, 
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[4]/div/div/div/div/div[2]/table/tr[15]/td[5]/img[2]', 
          2021)

#teacher trained CWSN:
scrapevar(driver, 
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[3]/div/div/div/div/div[2]/table/tr[11]/td[5]/img[2]', 
          2021)
#computer 
scrapevar(driver, 
          '/html/body/app-root/app-report-dashboard/mat-sidenav-container/mat-sidenav-content/app-static-report/div/mat-card-content/div[2]/div[4]/div/div/div/div/div[2]/table/tr[34]/td[5]/img[2]', 
          2021)


