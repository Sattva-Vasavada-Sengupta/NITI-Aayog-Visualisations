# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 10:46:16 2023

@author: Sattva Vasavada
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import geopandas as gpd
import seaborn as sns

#%%% #reading and combining data into a natoinal dataset. No need to run this code once
#the file is generated. 

# os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/Data/raw MA data CSVs")
# # Currently we are only concerned with UP and Bihar: state codes 9 and 10, respectively. 
# files = os.listdir() 

# data = pd.DataFrame()

# for filenum in files: 
#     df = pd.read_csv(str(filenum))
#     print(filenum, len(df))
#     data = data.append(df)
    
# os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
# data.to_csv("allindia_merged.csv")
    
#%%% Start analysis: Read data first that was saved above. 

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
data = pd.read_csv("allindia_merged.csv") #created in the above code block. 

fullcolumn_list = list(data.columns)
#select relevant columns for now. New columns can always be added later. 

data = data[['state_code', 'state_name',
             'district_code', 'district_name',
             'sub_district_code','sub_district_name',
             'block_code', 'block_name',
             'gp_code','gp_name',
             'village_code', 'village_name',
             'is_atm_available', 'distance_of_atm',
             'is_bank_available', 'distance_of_banks', 'is_bank_buss_correspondent_with_internet',
             'is_broadband_available', 
             'village_latitude', 'village_longitude',
             
             #demographics 
             'total_population', 'total_hhd',
             'male_population', 'female_population', 
             'total_male_child_age_bw_0_6', 'total_female_child_age_bw_0_6',
             
             #basic village infra
             'is_fertilizer_shop_available', 
             'is_village_connected_to_all_weather_road', 'distance_of_all_weather_road',
             'availability_of_public_transport', 'distance_of_public_transport', 
             'availablility_hours_of_domestic_electricity', 
             'availability_of_primary_school', 'distance_of_primary_school',
             'availability_of_middle_school', 'distance_of_middle_school',
             'availability_of_high_school', 'distance_of_high_school', 
             'availability_of_market', 'distance_of_market', 
             'availability_of_phc_chc', 'distance_of_phc_chc',
             
             #toilet 
             'primary_school_toilet', 'availability_of_drainage_system',
             'is_community_waste_disposal_system', 
             'total_hhd_not_having_sanitary_latrines', 
             
             #drinking water
             'availability_of_piped_tap_water', 'distance_of_piped_tap_water', 
             'is_primary_school_have_drinking_water',
             'total_hhd_having_piped_water_connection', 
             
             #Aaganwadi data
             'is_aanganwadi_centre_available', 'distance_of_aanganwadi_centre',
             'is_early_childhood_edu_provided_in_anganwadi', 
             'total_childs_aged_0_to_3_years', 'total_childs_aged_0_to_3_years_reg_under_aanganwadi',
             'total_childs_aged_3_to_6_years_reg_under_aanganwadi', 
             'total_no_of_registered_children_in_anganwadi', 
             
             #status of health - of people, not health infra. 
             'total_childs_aged_0_to_3_years_immunized', 
             'total_anemic_pregnant_women', 'total_anemic_adolescent_girls',
             'total_underweight_child_age_under_6_years',
             'total_no_of_lactating_mothers', 'total_no_of_pregnant_women', 
             'total_no_of_newly_born_children', 'total_no_of_newly_born_underweight_children',
             
             #nutrition
             'total_no_of_children_in_icds_cas', 'availability_of_mid_day_meal_scheme',
             'is_pds_available', 'distance_of_pds_office', 
             'gp_total_hhd_eligible_under_nfsa', 'gp_total_hhd_receiving_food_grains_from_fps',
             
             #SHG Indicators
             'total_shg', 'total_hhd_mobilized_into_shg', 'total_no_of_shg_promoted',
             'total_shg_accessed_bank_loans', 
             
             #PMAY
             'total_hhd_have_got_pmay_house', 'total_hhd_in_pmay_permanent_wait_list',
             'total_hhd_with_kuccha_wall_kuccha_roof',
             
             #FPOs:
             'availability_of_fpos_pacs', 'availability_of_food_storage_warehouse', 
             'distance_of_food_storage_warehouse', 'availability_of_farm_gate_processing',
             'availability_of_custom_hiring_centre_agri_equipment',
             
             #Groundwater:
             'availability_of_watershed_dev_project', 'availability_of_rain_harvest_system'
             
             ]]
   
#total population has one string. We convert it to a nan value. 
data.total_population = pd.to_numeric(data.total_population, errors = 'coerce')

#check number of nans in village lat long: 
print(data.village_latitude.isna().sum())
print(data.village_longitude.isna().sum())

#i mean, could've done without defining a function too. 
def column_lower(column_name):
    return data[column_name].str.lower()

#create a list of all columns that need to be converted to lowercase. 
columns_to_lower = ['state_name', 'district_name', 'block_name', 'sub_district_name', 
                    'gp_name', 'village_name']

#make them lower case. 
for column_name in columns_to_lower:
    data[column_name] = column_lower(column_name)

#%%% cleaning data part 1: checking if variable is a dummy or not. 

def checkdummy(column_name):
    print(Counter(data[column_name].astype(str)))
    return None

dummies_in_question = ['is_atm_available', 
                       'is_bank_available', 'is_bank_buss_correspondent_with_internet',
                       'is_broadband_available', 
                       'is_fertilizer_shop_available', 'is_fertilizer_shop_available',
                       'is_fertilizer_shop_available', 
                       'availability_of_primary_school', 
                       'availability_of_middle_school', 
                       'availability_of_high_school',
                       'availability_of_market',
                       'availability_of_phc_chc',
                       'availability_of_piped_tap_water',
                       'is_aanganwadi_centre_available', 
                       'primary_school_toilet', 'availability_of_drainage_system',
                       'is_community_waste_disposal_system',
                       'is_early_childhood_edu_provided_in_anganwadi', 
                       'availability_of_mid_day_meal_scheme',
                       'is_pds_available',
                       'is_village_connected_to_all_weather_road',
                       'availability_of_fpos_pacs', 'availability_of_food_storage_warehouse', 
                       'availability_of_farm_gate_processing',
                       'availability_of_custom_hiring_centre_agri_equipment',
                       'availability_of_watershed_dev_project', 'availability_of_rain_harvest_system']

##commented out for now, but if we add more dummies/want to check again, we can 
##uncomment the for-loop below. 

# for dummy in dummies_in_question:
#     print(dummy), checkdummy(dummy)
    
#final dummy list: remove those which are coded 1-4. These will have to be converted to 
#dummies, but the proceedure will depend on how they are coded, and hence will have to 
#be manually done with explaination for why they were coded the way they were. 

final_dummy_list = ['is_atm_available', 
                    'is_bank_available', 'is_bank_buss_correspondent_with_internet',
                    'is_broadband_available', 
                    'is_fertilizer_shop_available', 'is_fertilizer_shop_available',
                    'is_fertilizer_shop_available', 
                    'availability_of_primary_school', 
                    'availability_of_middle_school', 
                    'availability_of_high_school',
                    'is_aanganwadi_centre_available', 
                    'is_community_waste_disposal_system',
                    'is_early_childhood_edu_provided_in_anganwadi', 
                    'is_pds_available',
                    'is_village_connected_to_all_weather_road',
                    'availability_of_food_storage_warehouse', 
                    'availability_of_farm_gate_processing',
                    'availability_of_custom_hiring_centre_agri_equipment',
                    'availability_of_watershed_dev_project', 'availability_of_rain_harvest_system']
 
print("\n Checking final dummy list once, before converting to 0/1s")
# for dummy in final_dummy_list:
#     print(dummy), checkdummy(dummy)
    
#remove variables from list above and add them here. Also add other variables that 
#you think are coded differntly: distance of atm, but coded 1-5. Even if the questionaire
#says coded 1-5, still good to check. 

coded_differntly_list = ['distance_of_atm', 'distance_of_banks', 
                        'distance_of_all_weather_road',
                        'distance_of_public_transport', 
                        'availablility_hours_of_domestic_electricity', 
                        'distance_of_primary_school',
                        'is_primary_school_have_drinking_water',
                        'distance_of_middle_school',
                        'distance_of_high_school', 
                        'availability_of_market', 'distance_of_market', 
                        'availability_of_phc_chc', 'distance_of_phc_chc',
                        'availability_of_piped_tap_water', 'distance_of_piped_tap_water',  
                        'distance_of_pds_office',
                        'primary_school_toilet',  
                        'availability_of_drainage_system',
                        'availability_of_mid_day_meal_scheme',
                        'availability_of_fpos_pacs',
                        'distance_of_aanganwadi_centre', 
                        'distance_of_food_storage_warehouse']

print("\nChecking final coded differntly list once, before processing them manually")
# for dummy in coded_differntly_list:
#     print(dummy), checkdummy(dummy)

#%%% #cleaning data part 2: converting dummies

#1 is yes, 2 is no. Source: English Questionaire. 
    
def dummy_conversion(column_name):
    column_name_cleaned = column_name + "_cleaned"
    data.loc[data[column_name] == 1, column_name_cleaned] = 1
    data.loc[data[column_name] == 2, column_name_cleaned] = 0
    return None

for dummy in final_dummy_list:
    dummy_conversion(dummy)
    
#%%% cleaning data part 4: converting differntly coded variables into dummies

differnt_coded_list_nondistance = ['availablility_hours_of_domestic_electricity', 
                       'is_primary_school_have_drinking_water', 
                       'availability_of_market', 
                       'availability_of_phc_chc', 
                       'availability_of_piped_tap_water',
                       'primary_school_toilet',  
                       'availability_of_drainage_system',
                       'availability_of_mid_day_meal_scheme',
                       'availability_of_fpos_pacs']

#Method: Check questionaire, and then for each variable, write down what the code is
#and why it is so. 

# 1. availablility_hours_of_domestic_electricity
data.loc[data['availablility_hours_of_domestic_electricity'] == 1, 
         'availablility_hours_of_domestic_electricity_cleaned'] = 2.5
data.loc[data['availablility_hours_of_domestic_electricity'] == 2, 
         'availablility_hours_of_domestic_electricity_cleaned'] = 6
data.loc[data['availablility_hours_of_domestic_electricity'] == 3, 
         'availablility_hours_of_domestic_electricity_cleaned'] = 10
data.loc[data['availablility_hours_of_domestic_electricity'] == 4, 
         'availablility_hours_of_domestic_electricity_cleaned'] = 12
data.loc[data['availablility_hours_of_domestic_electricity'] == 5, 
         'availablility_hours_of_domestic_electricity_cleaned'] = 0

# 2. is_primary_school_have_drinking_water
#not differently coded. It is the number of schools in that village that that have drinking water. 

#3. Availability of market
# 4 means no availability of any differnet market (mandi, daily market, weekly market). 
#hence 0 means no market, 1 means some market. 
data.loc[data['availability_of_market'] == 1, 
         'availability_of_market_cleaned'] = 1
data.loc[data['availability_of_market'] == 2, 
         'availability_of_market_cleaned'] = 1
data.loc[data['availability_of_market'] == 3, 
         'availability_of_market_cleaned'] = 1
data.loc[data['availability_of_market'] == 4, 
         'availability_of_market_cleaned'] = 0

#4. availability_of_phc_chc
#unsure about how this is coded. It is difficult to parse this. 

#5. availability_of_piped_tap_water
#unsure how this is coded. 

#6. primary_school_toilet
#unsure how this is coded. 

#7. availability_of_drainage_system
#5 means no drainage. Others mean some form of drainage. 
data.loc[data['availability_of_drainage_system'] == 1, 
         'availability_of_drainage_system_cleaned'] = 1
data.loc[data['availability_of_drainage_system'] == 2, 
         'availability_of_drainage_system_cleaned'] = 1
data.loc[data['availability_of_drainage_system'] == 3, 
         'availability_of_drainage_system_cleaned'] = 1
data.loc[data['availability_of_drainage_system'] == 4, 
         'availability_of_drainage_system_cleaned'] = 1
data.loc[data['availability_of_drainage_system'] == 5, 
         'availability_of_drainage_system_cleaned'] = 0

#8. availability_of_mid_day_meal_scheme
#could not find this in the questionaire. 
#but assuming 1 is yes, and 0 and 2 are no, we could go ahead. 

data.loc[data['availability_of_mid_day_meal_scheme'] == 1, 
         'availability_of_mid_day_meal_scheme_cleaned'] = 1
data.loc[data['availability_of_mid_day_meal_scheme'] == 2, 
         'availability_of_mid_day_meal_scheme_cleaned'] = 0
data.loc[data['availability_of_mid_day_meal_scheme'] == 0, 
         'availability_of_mid_day_meal_scheme_cleaned'] = 0 

#9. availability_of_fpos_pacs
# 4 is neither FPO or PACS. Other means alteast one of them present. 
data.loc[data['availability_of_fpos_pacs'] == 1, 
         'availability_of_fpos_pacs_cleaned'] = 1
data.loc[data['availability_of_fpos_pacs'] == 2, 
         'availability_of_fpos_pacs_cleaned'] = 1
data.loc[data['availability_of_fpos_pacs'] == 3, 
         'availability_of_fpos_pacs_cleaned'] = 1
data.loc[data['availability_of_fpos_pacs'] == 4, 
         'availability_of_fpos_pacs_cleaned'] = 0

diff_coded_vars_list = ['availability_of_market',  
                       'availability_of_drainage_system',
                       'availability_of_mid_day_meal_scheme',
                       'availability_of_fpos_pacs']

diff_coded_vars_list_cleaned = [x + '_cleaned' for x in diff_coded_vars_list]

#%%% cleaning data part 5: converting distance categories into distance ranges.  

#Went through questionaiare. All distance codes except two are the same. 
#The codes are:
    
'''
<1 km: 1
1-2 km: 2
2-5 km: 3
5-10 km: 4
>10 km: 5
'''

#There are two variabels whose distances are defined differently. 
#For PHC CHC distace, the code in the questionaire has distance for each center not 
#available. But the dataset does not distinguish what is and what isn't available. 

#For degree college, codes are 1-6. Have a look at them if you want to work with them later. 

def distance_conversion_min(varname):
    varname_cleaned_min = varname + ("_cleaned_min")
    data.loc[data[varname] == 1, varname_cleaned_min] = 0.1
    data.loc[data[varname] == 2, varname_cleaned_min] = 1
    data.loc[data[varname] == 3, varname_cleaned_min] = 2
    data.loc[data[varname] == 4, varname_cleaned_min] = 5
    data.loc[data[varname] == 5, varname_cleaned_min] = 10

def distance_conversion_max(varname):
    varname_cleaned_min = varname + ("_cleaned_max")
    data.loc[data[varname] == 1, varname_cleaned_min] = 1
    data.loc[data[varname] == 2, varname_cleaned_min] = 2
    data.loc[data[varname] == 3, varname_cleaned_min] = 5
    data.loc[data[varname] == 4, varname_cleaned_min] = 10
    data.loc[data[varname] == 5, varname_cleaned_min] = 15 #>10, so put 15. Not sure if 
    #this is correct, however. 
    
def distance_conversion_avg(varname):
    varname_cleaned_min = varname + ("_cleaned_avg")
    data.loc[data[varname] == 1, varname_cleaned_min] = 0.5
    data.loc[data[varname] == 2, varname_cleaned_min] = 1.5
    data.loc[data[varname] == 3, varname_cleaned_min] = 3.5
    data.loc[data[varname] == 4, varname_cleaned_min] = 7.5
    data.loc[data[varname] == 5, varname_cleaned_min] = 10

#make a list of all variables referring to distance from a place. 
distance_vars_list = ['distance_of_atm', 
                      'distance_of_banks', 
                      'distance_of_all_weather_road',
                      'distance_of_public_transport', 
                      'distance_of_primary_school',
                      'distance_of_middle_school',
                      'distance_of_high_school', 
                      'distance_of_market', 
                      'distance_of_phc_chc',
                      'distance_of_piped_tap_water',  
                      'distance_of_pds_office',
                      'distance_of_aanganwadi_centre', 
                      'distance_of_food_storage_warehouse']

for distance_var in distance_vars_list:
    distance_conversion_min(distance_var)
    distance_conversion_max(distance_var)
    distance_conversion_avg(distance_var)
    
#%%% cleaning part 6: create percentages at the village level from totals. 

#These variables need to be converted into percentages for meaningful insights. 

vars_to_percent_list = ['total_population', 'total_hhd',
                    'male_population', 'female_population', 
                    'total_childs_aged_0_to_3_years', 
                    'total_male_child_age_bw_0_6', 'total_female_child_age_bw_0_6',
                    'total_hhd_not_having_sanitary_latrines', 
                    'total_hhd_having_piped_water_connection',
                    'total_childs_aged_0_to_3_years', 
                    'total_childs_aged_0_to_3_years_reg_under_aanganwadi',
                    #'total_childs_aged_3_to_6_years_reg_under_aanganwadi', 
                    #'total_no_of_registered_children_in_anganwadi', 
                    'total_childs_aged_0_to_3_years_immunized', 
                    'total_anemic_pregnant_women', 'total_anemic_adolescent_girls',
                    'total_underweight_child_age_under_6_years',
                    'total_no_of_lactating_mothers', 
                    'total_no_of_pregnant_women', 
                    'total_no_of_newly_born_children', 
                    'total_no_of_newly_born_underweight_children',
                    'total_no_of_children_in_icds_cas',
                    'gp_total_hhd_eligible_under_nfsa', #at the gp level?
                    'gp_total_hhd_receiving_food_grains_from_fps',
                    'total_shg', 'total_hhd_mobilized_into_shg', 
                    'total_no_of_shg_promoted',
                    'total_shg_accessed_bank_loans', 
                    'total_hhd_have_got_pmay_house', 
                    'total_hhd_in_pmay_permanent_wait_list',
                    'total_hhd_with_kuccha_wall_kuccha_roof']

def create_percent_var_hhd(varname):
    hhd_varname = "percent" + varname[5:]
    # print(hhd_varname)
    data[hhd_varname] = np.round((data[varname] / data['total_hhd']) *100, 2)
    
def create_percent_var_women(varname):
    hhd_varname = "percent" + varname[5:]
    # print(hhd_varname)
    data[hhd_varname] = np.round((data[varname] / data['female_population']) *100, 2)
    
def create_percent_var_childs_aged_0_to_3(varname):
    hhd_varname = "percent" + varname[5:]
    # print(hhd_varname)
    data[hhd_varname] = np.round((data[varname] / data['total_childs_aged_0_to_3_years']) *100, 2)

hhd_varlist = ['total_hhd_not_having_sanitary_latrines',
               'total_hhd_having_piped_water_connection',
               'total_hhd_mobilized_into_shg',
               'total_hhd_have_got_pmay_house',
               'total_hhd_in_pmay_permanent_wait_list',
               'total_hhd_with_kuccha_wall_kuccha_roof']

childs_aged_0_to_3_varlist = ['total_childs_aged_0_to_3_years_reg_under_aanganwadi',
                              'total_childs_aged_0_to_3_years_immunized']

hhd_percent_varlist = list()
women_percent_varlist = list()
child_0_to_3_percent_varlist = list()

for hhd_varname in hhd_varlist:
    create_percent_var_hhd(hhd_varname)
    hhd_percent_varlist.append("percent" + hhd_varname[5:])
    
for child_0_to_3 in childs_aged_0_to_3_varlist:
    create_percent_var_childs_aged_0_to_3(child_0_to_3)
    child_0_to_3_percent_varlist.append("percent" + child_0_to_3[5:])

#manual percentage variable creations:
    
data['total_childs_aged_0_to_6'] = data['total_male_child_age_bw_0_6'] + data['total_female_child_age_bw_0_6']

data['percent_underweight_child_age_under_6_years'] = np.round((data['total_underweight_child_age_under_6_years'] / data['total_childs_aged_0_to_6']) *100, 2)

data['percent_no_of_newly_born_underweight_children'] = np.round((data['total_no_of_newly_born_underweight_children'] / data['total_no_of_newly_born_children']) *100, 2)

data['percent_anemic_pregnant_women'] = np.round((data['total_anemic_pregnant_women'] / data['total_no_of_pregnant_women']) *100, 2)

data['percent_shg_accessed_bank_loans'] = np.round((data['total_shg_accessed_bank_loans'] / data['total_shg']) *100, 2)

#Create a list of variables that have percentage terms. These will be treated differntly
# - we won't multiply these by 100, unlike dummy means that we calcualte below. 

percent_list = ['percent_underweight_child_age_under_6_years',
                'percent_no_of_newly_born_underweight_children',
                'percent_anemic_pregnant_women',
                'percent_shg_accessed_bank_loans'] + hhd_percent_varlist + women_percent_varlist + child_0_to_3_percent_varlist 

##Commented out: was just checking if the means made sense. Can uncomment if you want
## to check if the percents were created correctly or not. 

# for var in percent_list:
#     print(var, data[var].mean())

#%%% Convert all means created above into percentages: 
    
#that is, we convert 
#means of dummies into percentages and round them to 2 places. For variables that were 
#already percentages, we round them 2 decimals. 

dummy_list = ['is_atm_available', 
            'is_bank_available', 'is_bank_buss_correspondent_with_internet',
            'is_broadband_available', 
            'is_fertilizer_shop_available', 
            'availability_of_primary_school', 
            'availability_of_middle_school', 
            'availability_of_high_school',
            'is_aanganwadi_centre_available', 
            'is_community_waste_disposal_system',
            'is_early_childhood_edu_provided_in_anganwadi', 
            'is_pds_available',
            'is_village_connected_to_all_weather_road',
            'availability_of_food_storage_warehouse', 
            'availability_of_farm_gate_processing',
            'availability_of_custom_hiring_centre_agri_equipment',
            'availability_of_watershed_dev_project', 'availability_of_rain_harvest_system']

#all dummies that were transformed from 2/1 to 0/1 respectively were called 
#dummy name + _cleaned, so we create dummy names that reflect the new ones. 

dummy_list_cleaned = [x + '_cleaned' for x in dummy_list]

#we can also take means of percentages of variables at the village level. 
#The percent list is defined above. All variables here can be averaged at the block level. 
#diff_coded_vars_list_cleaned are dummies that I created (any market avaialable, etc). 

mean_list = dummy_list_cleaned + percent_list + diff_coded_vars_list_cleaned

#dummy mean converted to percentages. 
for column in dummy_list_cleaned:
    data[column] = np.round(data[column] * 100, 2)

#percentages remain as percentages, but are rounded. 
for column in percent_list:
    data[column] = np.round(data[column], 2)
 
#dummies that I created - converted to percentages
for column in diff_coded_vars_list_cleaned:
    data[column] = np.round(data[column] * 100, 2)
       
#%%% Merge village level data with aspirational blocks list: 
#we know which blocks are ABs - we read the excel file here.  

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data")
abp_blocks = pd.read_excel("_List of 500 Aspirational Blocks_112 Aspirational Districts_ABP & ADP (1).xlsx")
abp_blocks.columns = abp_blocks.columns.str.lower() #convert column names to lower. 
abp_blocks.drop("s.no.", axis = 1, inplace = True) #drop index column. 
abp_blocks.drop(abp_blocks.tail(1).index,inplace=True) #drop last row: it is only a nan row. 

#all variables (columns) convert to lower case to merge on state and block names. 
for column in abp_blocks.columns:
    abp_blocks[column] = abp_blocks[column].str.lower()

#create a dummy = 1 if block is aspirational. Because all blocks in the abp_blocks 
#dataset are aspirational blocks, the entire column is = 1. We will assign 0's below
abp_blocks['aspirational_block'] = 1   

#%%% Combining AB list with main data at the village level. 

data = pd.merge(data, abp_blocks, left_on = ['state_name', 
                                             'block_name'],
                right_on = ['state', 'block'], how = 'outer')

data['aspirational_block'].fillna(0, inplace = True)

data.loc[data['aspirational_block'] == 0, "aspirational_block_text"] = "Non-AB"
data.loc[data['aspirational_block'] == 1, 'aspirational_block_text'] = "AB"

#%%% Aspirational Block means at the state level using village level data. 

#These lists were defined above, and were used to create means at the block level. 
#the variable names remain the same for creating means at the state level. 

mean_list = dummy_list_cleaned + percent_list + diff_coded_vars_list_cleaned

df_state = data.groupby(['state_name', 'aspirational_block'])[mean_list].mean()
india_avg = data.groupby('aspirational_block')[mean_list].mean()
#dummy mean at state level converted to percentages. 

#reset index - index converted to columns. 
df_state.reset_index(drop = False, inplace = True) #make index to columns. 
india_avg.reset_index(drop = False, inplace = True) #make index to columns. 

india_avg['state_name'] = "india"

df_state = df_state.append(india_avg)

#Add a string column for making box plots. 
df_state.loc[df_state['aspirational_block'] == 0, "aspirational_block_text"] = "Non-AB"
df_state.loc[df_state['aspirational_block'] == 1, 'aspirational_block_text'] = "AB"

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
df_state.to_csv("statelevel_abp.csv", index = False)

#%%% getting differnces between ABs and Non ABs at the state level. 

df_state.sort_values(['state_name', 'aspirational_block'], inplace = True)

#return diff of difference between AB and Non AB at the state level for a variable: 
def get_topdiff_3(varname):
    varname_diff = varname + '_diff'
    df_state[varname_diff] = df_state.groupby(['state_name'])[varname].diff()
    df = df_state[['state_name', varname_diff]]
    df.dropna(inplace = True)
    df.sort_values(varname_diff, inplace = True)
    
    os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
    # df.to_csv(varname_diff + ".csv", index = False)
    return df

def get_boxplot(varname, ylabel):
    os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
    sns.boxplot(df_block, y = df_block[varname], x = df_block['aspirational_block_text'], 
                showfliers=False).set(ylabel = ylabel, xlabel = "")
    plt.savefig(ylabel + "_fig.png")
    plt.show()
    return None

#Get differences and box plots:
    
#Infra: All Weather Road
get_topdiff_3('is_village_connected_to_all_weather_road_cleaned')   
get_boxplot("is_village_connected_to_all_weather_road_cleaned",
            "Connected to All Weather Road")

#Infra: Availability of Market:
get_topdiff_3('availability_of_market_cleaned')   
get_boxplot("availability_of_market_cleaned", "Market Available")

#Sanitation: Percent HH NOT having sanitary laterines
get_topdiff_3('percent_hhd_not_having_sanitary_latrines') 
get_boxplot("percent_hhd_not_having_sanitary_latrines", "HH NOT have latrines")

#Sanitation: Availability of any drainage system: 
get_topdiff_3('availability_of_drainage_system_cleaned')   
get_boxplot("availability_of_drainage_system_cleaned", "Any Drainage System")
  
#Water: Percent HH having piped water.  
get_topdiff_3('percent_hhd_having_piped_water_connection')
get_boxplot("percent_hhd_having_piped_water_connection", "Piped Water Connections")

# Aanganwadi: Percent having AAW 
get_topdiff_3('is_aanganwadi_centre_available_cleaned')  
get_boxplot("is_aanganwadi_centre_available_cleaned", "AAW Center")

# Aanganwadi: Enrollement rates
get_topdiff_3('percent_childs_aged_0_to_3_years_reg_under_aanganwadi')  
get_boxplot("percent_childs_aged_0_to_3_years_reg_under_aanganwadi", "AAW Enrollment (0-3 years)")

# Health Status: Pregnant Anemic women
get_topdiff_3('percent_anemic_pregnant_women')  
get_boxplot("percent_anemic_pregnant_women", "Anemic Pregnant Women")

# Health status: percent underweight
get_topdiff_3('percent_underweight_child_age_under_6_years')  
get_boxplot("percent_underweight_child_age_under_6_years", "Underweight children (below 6)")

# Nutrition: Mid day meals
get_topdiff_3('availability_of_mid_day_meal_scheme_cleaned')  
get_boxplot("availability_of_mid_day_meal_scheme_cleaned", "Mid Day Meals Available")

# Nutritoin: PDS availability
get_topdiff_3('is_pds_available_cleaned')  
get_boxplot("is_pds_available_cleaned", "PDS Shop Available in Village")

# SWM:
get_topdiff_3('is_community_waste_disposal_system_cleaned')  
get_boxplot("is_community_waste_disposal_system_cleaned", "Community Waste Disposal System")

# SHGS:
get_topdiff_3('percent_hhd_mobilized_into_shg')  
get_boxplot("percent_hhd_mobilized_into_shg", "Percent HH mobilised into SHGs")

# SHGs:
get_topdiff_3('percent_shg_accessed_bank_loans')  
get_boxplot("percent_shg_accessed_bank_loans", "Percent SHGs accessing bank loans")

# Pmay:
get_topdiff_3('percent_hhd_have_got_pmay_house')  
get_boxplot("percent_hhd_have_got_pmay_house", "Percent HH having PMAY House")

# FPOs:
get_topdiff_3('availability_of_fpos_pacs_cleaned')  
get_boxplot("availability_of_fpos_pacs_cleaned", "Any FPO-PACS available in village")

# Groundwater:
get_topdiff_3('availability_of_watershed_dev_project_cleaned')  
get_boxplot("availability_of_watershed_dev_project_cleaned", "Watershed project in village")


#%%% MA data means at the state level: used for visualising stuff: agnostic of 
#AB or non-AB. Only do means at the state level. 

#These lists below were defined above, and were used to create means at the block level. 
#the variable names remain the same for creating means at the state level. 

mean_list = dummy_list_cleaned + percent_list + diff_coded_vars_list_cleaned

df = data.groupby(['state_name'])[mean_list].mean()

#reset index - index converted to columns. 
df.reset_index(drop = False, inplace = True) #make index to columns. 

#save state level means (agnostic of AB or non-AB).
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
df.to_csv("stateindicatorvalues_MA2020.csv", index = False)

#%%% District Level Means: Agnostic to AB. 
#we shall highlight districts with ABs later. 

#These lists below were defined above, and were used to create means at the block level. 
#the variable names remain the same for creating means at the state level. 

mean_list = dummy_list_cleaned + percent_list + diff_coded_vars_list_cleaned    

#create district level percentages. 
df_district = data.groupby(['state_name', 'state_code', 
                            'district_name', 'district_code'])[mean_list].mean()

#
df_district.reset_index(inplace = True, drop = False)

#%%% Merging with number of ABs at district level. 

#first we calculate number of ABs at the district level. 

distblock_count = pd.DataFrame(abp_blocks.groupby(['district'])['block'].count())
distblock_count.reset_index(drop = False, inplace = True)
distblock_count.columns = ['district', 'block_count']

df_district = pd.merge(df_district, distblock_count, left_on = ['district_name'], 
                right_on = ['district'], how = 'left')
df_district.drop(['district'], axis = 1, inplace = True)
df_district.block_count.fillna(0, inplace = True)

#%%% Visualise district level means: using SHRUG PC 11. 
    
#We have GIS files from SHRUG. They are 2011 district shapefiles. Our data is 2020. 

#fortunately, we have district codes. We have LGD that maps latest district codes 
#to census 2011 dist codes. SHRUG uses 2011 dist codes. Then we merge on dist code. 
#Then we visualise. 

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data")
lgd = pd.read_csv('Local Gov Directory_LGD_30_06_23.csv')

lgd.columns = lgd.columns.str.lower()
lgd.drop(['s.no.'], axis = 1, inplace = True)
lgd.columns = ['state_code_lgd', 'state_name_lgd', 
               'district_code_lgd', 'district_name_lgd', 
               'censuscode_2001', 'censuscode_2011']
    
lgd.state_name_lgd = lgd.state_name_lgd.str.lower()
lgd.district_name_lgd = lgd.district_name_lgd.str.lower()

#merge district means dataset created in the code block above with lgd. 

df_district = pd.merge(df_district, lgd, left_on = ["state_code", "district_code"],
                       right_on  = ['state_code_lgd', 'district_code_lgd'], 
                       how = 'outer')

#I ran the merge above, and saw that all districts from MA merged perfectly with 
#LGD. The LGD, however, had a few districts that were not present in MA 2020. 

#we keep these districts because keeping them does not harm us. 

#we remove two rows where there are nans in the entire row. Possibly because there 
#are some blanks spaces in the LGD excel file. 

df_district.dropna(subset = ['district_code_lgd'], inplace = True)

#column is float, so convert to int. 
df_district.district_code_lgd = df_district.district_code_lgd.astype(int) 
    
#read the shapefile and do the routine things. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/District GIS Files/SHRUG PC 11")
distmap = gpd.read_file("district.shp")

#distmap pc11 id is str. Convert to int. 
distmap.pc11_d_id = distmap.pc11_d_id.astype(int)

#merge distmap with the df_district on census 2011 district codes

distmap = pd.merge(df_district, distmap, left_on = ['district_code_lgd'],
                right_on = ['pc11_d_id'], how = 'outer')

test = distmap.drop(['geometry'], axis = 1)

distmap = gpd.GeoDataFrame(distmap, crs="EPSG:4326")

#%%% Merging with shapefiles provided by Mr. Saruabh Thurkral, NITI. 

#read NITI given shapefile: [add source name here]

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/District GIS Files/NITI Given Files")
distmap = gpd.read_file('DISTRICT_BOUNDARY.shp')
distmap.columns = distmap.columns.str.lower()
distmap.columns = ['district', 'state', 'remarks', 'state_lgd', 'district_lgd', 'shape_leng',
       'shape_area', 'geometry']

distmap.district_lgd = distmap.district_lgd.astype(float)

#merge with district level data
distmap = pd.merge(df_district, distmap, left_on = ['district_code'],
         right_on = ['district_lgd'], how = 'outer')

distmap = gpd.GeoDataFrame(distmap, crs="EPSG:32748")

#%%% Make dist level maps () at the state level: 

#at the national level, this is hard to visualise. 

plt.figure(figsize=(10, 10))

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/Planning Secretaries Viz Output Files")

def distplot(varname, varlabel, positive_or_negative):
    for state in set(distmap.state_name):
        if str(state) == "nan":
            continue
        
        if positive_or_negative == "positive":
            cmap_color = "RdYlGn"
        elif positive_or_negative == "negative":
            cmap_color = "RdYlGn_r"
        
        try:
            ax = distmap[distmap.state_name == state].plot(column = varname, cmap = cmap_color, legend = True,
                          missing_kwds= dict(color = "lightgrey"))
            distmap.loc[(distmap.block_count > 0) &
                        (distmap.state_name == state)].plot(ax = ax, facecolor='none', edgecolor='black', linewidth = 1, alpha = 1)
            
            for block_count, geometry in zip(distmap[(distmap.state_name == state) &
                                                     (distmap.block_count > 0)]['block_count'], 
                                             distmap[(distmap.state_name == state) & 
                                                     (distmap.block_count > 0)]['geometry']):
                ax.text(geometry.centroid.x, geometry.centroid.y, int(block_count), fontsize = 8, 
                        bbox={"facecolor":"orange", "alpha":0.5, "pad":0.8})
            
            plt.axis('off')
            plt.title(state.title() + ": " + varlabel)
            plt.figtext(0.5, 0.05, "Highlighted Districts:\nHave Atleast One AB.", ha="center",
                        fontsize=12, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
            plt.savefig(state + "_" + varlabel + "_distlevel.png", dpi = 1200)
            plt.close()
        except:
            continue
        
    print(varlabel + " over.")  
        
distplot("percent_anemic_pregnant_women", "Percent Anemic Pregnant Women", 
          "negative")

distplot("percent_underweight_child_age_under_6_years", "Percent Underweight children (below 6)", "negative")

distplot("availability_of_mid_day_meal_scheme_cleaned", "Percent Mid Day Meals Available","positive")

distplot("is_pds_available_cleaned", "Percent PDS Shop Available in Village",
          "positive")

distplot("percent_hhd_not_having_sanitary_latrines", "Percent HH with no latrines", "negative")

distplot("availability_of_drainage_system_cleaned", "Percent Village with Any Drainage System",
          "positive")

distplot("percent_hhd_having_piped_water_connection", "Percent Villages with Piped Water Connections",
          "positive") 

distplot("percent_hhd_mobilized_into_shg", "Percent HH mobilised into SHGs",
          "positive")

distplot("percent_shg_accessed_bank_loans", "Percent SHGs accessing bank loans", "positive")

#%%%


