# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:40:11 2023

@author: Sattva Vasavada
"""
import os
import pandas as pd
import numpy as np
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely
import mapclassify
import matplotlib.cm as cm
import matplotlib.patches as mpatches

#%%% Reading list of ABs. 

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data")
abp_blocks = pd.read_csv("AB_LGD Codes_500 Blocks.csv")
abp_blocks.columns = abp_blocks.columns.str.lower() #convert column names to lower. 
abp_blocks.drop("s.no.", axis = 1, inplace = True) #drop index column. 
 
#all variables (columns) convert to lower case to merge on state and block names. 
for column in ['state', 'district', 'block']:
    abp_blocks[column] = abp_blocks[column].str.lower()
    
abp_blocks.columns = ['statename_abp', 'districtname_abp', 'blockname_abp',
                      'statecode_lgd', 'districtcode_lgd', 'blockcode_lgd',
       'block version']

abp_blocks = abp_blocks[['statename_abp', 'districtname_abp', 'blockname_abp',
                      'statecode_lgd', 'districtcode_lgd', 'blockcode_lgd']]


#create a dummy = 1 if block is aspirational. Because all blocks in the abp_blocks 
#dataset are aspirational blocks, the entire column is = 1. We will assign 0's below
abp_blocks['aspirational_block'] = 1 

abp_blocks.loc[abp_blocks.statename_abp == "jammu & kashmir", "statename_abp"] = "jammu and kashmir" 

#%%% 

df = pd.DataFrame(abp_blocks.groupby('statename_abp')['blockname_abp'].count())
df.columns = ['block_count']
df.reset_index(drop = False, inplace = True)

df.loc[df.block_count <= 20, 'count_category'] = "0 - 20"
df.loc[(df.block_count > 20) &
       (df.block_count <= 40), 'count_category'] = "21 - 40"
df.loc[df.block_count > 40, 'count_category'] = "40+"

df1 = pd.DataFrame(df.groupby('count_category')['count_category'].count())
df1.columns = ['Number of States In Category']
df1.reset_index(drop = False, inplace = True)
df1.columns = ['Count Category', 'Number of States In Category']

df.columns = ['State Name', 'Number of Blocks Within State', 'Count Category']

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/AB List Output")
df1.to_csv('0_20_40_categorisation_abpblocks_aggregates.csv', index = False)
df.to_csv('0_20_40_categorisation_abpblocks_statewise.csv')

#%%% Block EDA: Number of blocks per state. 

#First we read the SHP - state map file. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/State GIS Files/NITI Files")
statemap = gpd.read_file("STATE_BOUNDARY.shp")
statemap.columns = statemap.columns.str.lower()
statemap.columns = ['statename_map', 'state_lgd', 'shape_leng', 'shape_area', 'geometry']
statemap = statemap[['statename_map', 'state_lgd', 'geometry']]

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data")
statelgd = pd.read_csv("state_LGD_04_07_23.csv")
statelgd.columns = ['s.no.', 'state_lgd', 'state version', 'statename_lgd',
        'state name (in local)', 'census2001_code', 'census2011_code',
        'state or ut', 'unnamed: 8']
statelgd = statelgd[['state_lgd', 'statename_lgd']]

statemap = pd.merge(statemap, statelgd, on = ['state_lgd'], how = 'outer')

statemap['statename_lgd'] = statemap['statename_lgd'].str.lower() #conver state names to lowercase. 

#drop disputed areas and fully nan rows. 
statemap = statemap.dropna(subset = ['statename_lgd'], axis = 0)
statemap = statemap[['statename_lgd', 'state_lgd', 'geometry']]

#group  by state and count number of blocks in eachs state. 
df = pd.DataFrame(abp_blocks.groupby(['state'])['block'].count()).reset_index(drop = False)
df.columns = ['statename_abp', 'block_count'] #rename as block_count. 

#the shapefile had different spellings of a couple of states. I change them here. 
df.loc[df['statename_abp'] == "dadra & nagar haveli and\ndaman & diu",
       'statename_abp'] = 'the dadra and nagar haveli and daman and diu'
df.loc[df['statename_abp'] == "jammu & kashmir",
       'statename_abp'] = 'jammu and kashmir'

#merge on state name for both. Keep the data on with the statemap column.  
statemap = pd.merge(df, statemap, left_on = ['statename_abp'], right_on = ['statename_lgd'],
                    how = 'outer')

statemap['block_count'] = statemap['block_count'].fillna(0)

#convert to geodata frame so that the .plot identifies the ploygons to be plotted. 
statemap = gpd.GeoDataFrame(statemap)

#number of aspirational blocks per state mapping. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/AB List Output")
ax = statemap.plot(column = "block_count",  cmap='viridis_r', legend = True)
statemap.plot(ax = ax, facecolor='none', edgecolor='black', linewidth = 0.5,alpha = 1)
for block_count, statename_lgd, geometry in zip(statemap['block_count'], 
                                                statemap['statename_lgd'],
                                 statemap['geometry']):
    #Dadra nagar and Haveli's representative point is far outside. So we use a centroid for it. 
    if statename_lgd != "the dadra and nagar haveli and daman and diu":
        plt.text(geometry.representative_point().x, geometry.representative_point().y, int(block_count), fontsize = 3, 
                bbox={"facecolor":"orange", "alpha":0.5, "pad":0.5})
    else:
        print(statename_lgd)
        plt.text(geometry.centroid.x, geometry.centroid.y, int(block_count), fontsize = 3, 
                bbox={"facecolor":"orange", "alpha":0.5, "pad":0.5})
        
plt.title("Number of Aspirational Blocks Per State")
plt.axis('off') #axis off means no lat long shown. not needed, so no show. 
plt.savefig("Number of Aspirational Blocks Per State.png", dpi = 1200) 
plt.show()

#%%% Map of number of ABs per district. 

#read NITI given shapefile: [add source name here]

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/District GIS Files/NITI Given Files")
distmap = gpd.read_file('DISTRICT_BOUNDARY.shp')
distmap.columns = distmap.columns.str.lower()
distmap.columns = ['districtname_map', 'statename_map', 'remarks', 'statecode_lgd', 'districtcode_lgd', 'shape_leng',
       'shape_area', 'geometry']
distmap = distmap[['districtname_map', 'districtcode_lgd', 'geometry']]

distmap.districtcode_lgd = distmap.districtcode_lgd.astype(float)

# #merge this with lgd. 
# os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data")
# distlgd = pd.read_csv("dist_LGD_30_06_23.csv")
# distlgd.columns = ['s.no.', 'state_lgd', 'statename_lgd', 'district_lgd', 'districtname_lgd',
#        'Census 2001 Code', 'Census 2011 Code']
# distlgd = distlgd[['state_lgd', 'statename_lgd', 'district_lgd', 'districtname_lgd']]
# distlgd['statename_lgd'] = distlgd['statename_lgd'].str.lower()
# distlgd['districtname_lgd'] = distlgd['districtname_lgd'].str.lower()

# distmap = pd.merge(distmap, distlgd, on = ['district_lgd'], how = 'outer')
# distmap = distmap[['districtname_lgd', 'district_lgd', 'state_lgd', 'statename_lgd',
#        'geometry']]

#make count of ABs per district. 
df = pd.DataFrame(abp_blocks.groupby(['statename_abp', 'districtname_abp'])['blockname_abp'].count())
df.reset_index(drop = False, inplace = True)
df.columns = ['statename_abp', 'districtname_abp', 'block_count']

df_codes = pd.DataFrame(abp_blocks.groupby(['statename_abp', 
                                            'districtname_abp', 
                                            'districtcode_lgd'])['aspirational_block'].mean())
df_codes.reset_index(inplace = True, drop = False)
df = pd.merge(df, df_codes, on = ['statename_abp', 'districtname_abp'])

# #rename districts of ABP: 
# #format: ABP dist name: correct LGD name
# namechange_dic = {'nicobar': 'nicobars', 
#                   'ss mankachar': 'south salmara mancachar', 
#                   'gaurella-pendra-marwahi': 'gaurella pendra marwahi', 
#                   'mohla-manpur- a chowki': 'mohla manpur ambagarh chouki', 
#                   'the dangs': 'dang', 
#                   'charkhi dadri': 'charki dadri', 
#                   'kalburgi': 'kalaburagi', 
#                   'kasargod': 'kasaragod', 
#                   # 'leh': '', 
#                   'khandwa(east nimar)': 'east nimar', 
#                   'gadhichiroli': 'gadchiroli', 
#                   'ngh ( garo region)': 'north garo hills', 
#                   'wjh( jaintia region)': 'west jaintia hills', 
#                   'keonjhar': 'kendujhar', 
#                   'nabarangapur': 'nabarangpur', 
#                   'raygada': 'rayagada', 
#                   'ferozpur': 'ferozepur', 
#                   's. madhopur': 'sawai madhopur', 
#                   'pudhukottai': 'pudukkottai', 
#                   'thiruvannamalai': 'tiruvannamalai', 
#                   'bhadradri-kothagudem': 'bhadradri kothagudem', 
#                   'kumuram bheem -asifabad': 'kumuram bheem asifabad', 
#                   'bijanaur': 'bijnor', 
#                   'pilbhit': 'pilibhit', 
#                   'st kabir nagar': 'sant kabeer nagar', 
#                   # 'st ravidas nagar': ''
#                   }

# for key in namechange_dic:
#     df.loc[df['districtname_abp'] == key,
#            'districtname_abp'] = namechange_dic[key]

#merge with district level data
distmap = pd.merge(df, distmap, on = ['districtcode_lgd'], how = 'outer')
# distmap = distmap.dropna(subset = ['districtname_abp', 'districtname_lgd'], axis = 0, thresh = 1)

distmap = gpd.GeoDataFrame(distmap)
#because all districts are merged (except 2, but that is okay for the map - not 
#much of a diff it will make), all non merged dist from LGD are non-AB dists. 

distmap['block_count'] = distmap['block_count'].fillna(0)

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/AB List Output")
distmap.plot(column = 'block_count', edgecolor = 'black', cmap='viridis_r', legend = True, scheme="User_Defined",
             classification_kwds=dict(bins=[0, 1, 2, 3, 6]), linewidth = 0.1)
cmap = cm.get_cmap('viridis_r')
p1 = mpatches.Patch(color=cmap(0.0), label='0')
p2 = mpatches.Patch(color=cmap(0.2), label='1')
p3 = mpatches.Patch(color=cmap(0.4), label='2')
p4 = mpatches.Patch(color=cmap(0.8), label='3')
p5 = mpatches.Patch(color=cmap(1.0), label='4+')
# p6 = mpatches.Patch(color=cmap(0.80), label='5')
# p7 = mpatches.Patch(color=cmap(1.0), label='6')

plt.legend(handles=[p1, p2, p3, p4, p5], 
           loc = 'center left',  bbox_to_anchor=(1.0, 0.5))
plt.axis('off')
plt.title("Number of Aspirational Blocks Per District")
plt.savefig("Number of Aspirational Blocks Per District.png", dpi = 1200) 
plt.show()

#%%% now for each state: 
    
#merge district lgd code with state name. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data")
distlgd = pd.read_csv("dist_LGD_30_06_23.csv")
distlgd = distlgd[['State Name', 'District Code', 'District Name']]
distlgd.columns = ['statename_lgd', 'districtcode_lgd', 'districtname_lgd']
distlgd['statename_lgd'] = distlgd['statename_lgd'].str.lower()
distlgd['districtname_lgd'] = distlgd['districtname_lgd'].str.lower()
distmap = pd.merge(distmap, distlgd, on = ['districtcode_lgd'], how = 'outer') 

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/AB List Output/Statewise Number of ABs")
for state in set(distmap.statename_lgd):
    if str(state) == "nan":
        continue
    distmap[distmap.statename_lgd == state].plot(column = 'block_count', edgecolor = 'black', cmap='viridis_r', legend = True, scheme="User_Defined",
                 classification_kwds=dict(bins=[0, 1, 2, 3, 6]), linewidth = 0.1)
    
    try:
        for block_count, geometry in zip(distmap[(distmap.statename_lgd == state) &
                                                 (distmap.block_count > 0)].block_count, 
                                         distmap[(distmap.statename_lgd == state) &
                                                 (distmap.block_count > 0)].geometry):
            try:
                plt.text(geometry.representative_point().x, geometry.representative_point().y, int(block_count), fontsize = 3)
            except: 
                pass
    except:
        print("what")
        pass
    cmap = cm.get_cmap('viridis_r')
    p1 = mpatches.Patch(color=cmap(0.0), label='0')
    p2 = mpatches.Patch(color=cmap(0.2), label='1')
    p3 = mpatches.Patch(color=cmap(0.4), label='2')
    p4 = mpatches.Patch(color=cmap(0.8), label='3')
    p5 = mpatches.Patch(color=cmap(1.0), label='4+')
    # p6 = mpatches.Patch(color=cmap(0.80), label='5')
    # p7 = mpatches.Patch(color=cmap(1.0), label='6')
    
    plt.legend(handles=[p1, p2, p3, p4, p5], 
               loc = 'center left',  bbox_to_anchor=(1.0, 0.5))
    plt.axis('off')
    plt.title(state.title() + ": Number of Aspirational Blocks Per District")
    num_abs = distmap[(distmap.statename_lgd == state)].groupby('statename_lgd')['block_count'].sum()[0]
    plt.figtext(0.5, 0.05, "Total Number of ABs: " + str(int(num_abs)), ha="center",
                fontsize=12, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    plt.savefig(state.lower() + "_Number of Aspirational Blocks Per District.png", dpi = 1200) 
    plt.show()

#%%% Bar Plot of number of ABs nationally, statewise: 

df = pd.DataFrame(abp_blocks.groupby('state')['block'].count())
df.reset_index(drop = False, inplace = True)
df.columns = ['statename_abp', 'block_count']
df.sort_values(by = ['block_count', 'statename_abp'], axis = 0, inplace = True, ascending = True)
df['statename_abp'] = df['statename_abp'].str.title() 
df.loc[df.statename_abp == "Andaman And Nicobar Islands", "statename_abp"] = "Andaman Nicobar"

plt.figure(figsize=(15, 10))
sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
ax = sns.barplot(y = df.statename_abp, x = df.block_count, orient = 'h', color = 'blue', alpha = 0.8)
ax.bar_label(ax.containers[0])
plt.xlabel('Number of Blocks')
plt.ylabel('State Name')
plt.title("Number of Aspirational Blocks Statewise")
plt.savefig("Number of Blocks per State Barplot.png", dpi = 1200)

#%%% Bar plot of number of ABs for each state: 
   
df = pd.DataFrame(abp_blocks.groupby(['state', 'district'])['block'].count())
df.reset_index(drop = False, inplace = True)
df.columns = ['statename_abp', 'districtname_abp', 'block_count']
df.sort_values(by = ['block_count', 'districtname_abp', 'statename_abp'], axis = 0, inplace = True, ascending = True)
df['statename_abp'] = df['statename_abp'].str.title() 
df['districtname_abp'] = df['districtname_abp'].str.title() 
df.loc[df.statename_abp == "Andaman And Nicobar Islands", "statename_abp"] = "Andaman Nicobar"

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/AB List Output/Statewise Number of ABs - Barplots")
for state in set(df.statename_abp):
    if state == 'Dadra & Nagar Haveli And\nDaman & Diu':
        continue
    
    plt.figure(figsize=(15, 10))
    sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})
    df_state = df[df.statename_abp == state]
    ax = sns.barplot(y = df_state.districtname_abp, x = df_state.block_count, orient = 'h', color = 'blue', alpha = 0.7)
    ax.bar_label(ax.containers[0])
    plt.xlabel('Number of Blocks')
    plt.ylabel('State Name')
    plt.title(state.title() + ": Number of Aspirational Blocks Districtwise")
    max_block_count = np.max(df_state.block_count)
    xticks_list = list(range(0, max_block_count + 1, 1))
    plt.xticks(xticks_list)
    plt.savefig(state + "_Number of Blocks per State Barplot.png", dpi = 1200)
    print(state, " over")
    
#%%% national map of where ABs are: 
    
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
data = pd.read_csv("allindia_merged.csv") #created in the above code block. 

data = data[['state_code', 'state_name',
             'district_code', 'district_name',
             'sub_district_code','sub_district_name',
             'block_code', 'block_name',
             'gp_code','gp_name',
             'village_code', 'village_name', 
             'village_latitude', 'village_longitude']]

#merge abp_blocks with LGD:
data = pd.merge(data, abp_blocks, left_on = ['block_code'], 
                                             right_on = ['blockcode_lgd'], 
                                             how = 'outer')
data.aspirational_block.fillna(0, inplace = True) #wherever not merged, that is a non asp block. 

df = data.groupby(['state_name', 'district_name', 
                 'block_name', 'block_code',
                 'aspirational_block'])[ 'village_latitude', 
                                        'village_longitude'].mean()



#%%% Cascading plot of number of blocks per district

#first groupby district to count number of blocks in each district. 
df = pd.DataFrame(abp_blocks.groupby(['district'])['block'].count())
df.columns = ['block_count']
df.reset_index(drop = False, inplace = True)

#then, each district has a block_count. It is anything between 1-6. Now, 
#we want to count the number of districts with a particular block count. 
#that is, count number of districts with number of blocks within district = 1 or 2 or. etc. 
#thus, groupby block_count, and count number of districts for each value of block_count.
df = pd.DataFrame(df.groupby(['block_count']).count())
df.reset_index(drop = False, inplace = True)
df.columns = ["Blocks Within District", 'Number of Districts']

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/AB List Output")
#Plot in a bar chart. 
sns.barplot(df['Blocks Within District'], df['Number of Districts'], color = 'blue', alpha = 0.8)
plt.xlabel("Number of Aspirational Blocks")
plt.ylabel("Number of Districts")
plt.title("Aspirational Blocks District Wise Counts")
plt.savefig("Aspirational Blocks District Wise Counts.png", dpi = 1200)
plt.show()

#%%% Indicators, statewise.

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
#this dataset was created in block_analysis_MA. It simply takes the means of values
#at the state level. 

#these are state level values for all villages within that state. It does not 
#differntiate between ABs and non-ABs. 
df = pd.read_csv("stateindicatorvalues_MA2020.csv")

#read shapefile again, because we made some changes to the shapefile above. We 
#start with afresh now. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/State GIS Files/Igismap")
statemap = gpd.read_file("Indian_States.shp")

#convert state names to lower case. 
statemap['st_nm'] = statemap['st_nm'].str.lower()

#the shapefile had different spellings of a couple of states. I change them here. 
statemap.loc[statemap['st_nm'] == "andaman & nicobar island", 'st_nm'] = 'andaman and nicobar islands'
statemap.loc[statemap['st_nm'] == "arunanchal pradesh", "st_nm"] = "arunachal pradesh"
statemap.loc[statemap['st_nm'] == "dadara & nagar havelli", "st_nm"] = "dadra & nagar haveli and\ndaman & diu"

#merge on state name. 
statemap = pd.merge(df, statemap, left_on = ['state_name'], right_on = ['st_nm'],
                    how = 'right')

#convert to geodataframe. 
statemap = gpd.GeoDataFrame(statemap, crs="EPSG:4326")

#define a function to plot maps. 
def createmap(varname, title, positive_or_negative):
    if positive_or_negative == "positive":
        cmap_color = "RdYlGn" #red to green. More is good, less is bad. 
    elif positive_or_negative == "negative":
        cmap_color = "RdYlGn_r" #green to red. More is bad, less is good. 
    statemap.plot(column = varname, cmap = cmap_color, legend = True,
                  missing_kwds= dict(color = "lightgrey"))
    plt.axis("off")
    plt.title(title)
    os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
    plt.savefig(title + "_statelevel.png", dpi = 1200)
    
#go ahead and create maps. 
createmap("percent_anemic_pregnant_women", "Percent Anemic Pregnant Women", 
          "negative")

createmap("percent_underweight_child_age_under_6_years", "Percent Underweight children (below 6)", "negative")

createmap("availability_of_mid_day_meal_scheme_cleaned", "Percent Mid Day Meals Available" ,"positive")

createmap("is_pds_available_cleaned", "Percent PDS Shop Available in Village", "positive")

createmap("percent_hhd_not_having_sanitary_latrines", "Percent HH with no latrines", "negative")

createmap("availability_of_drainage_system_cleaned", "Percent Village with Any Drainage System" ,"positive")

createmap("percent_hhd_having_piped_water_connection", "Percent Villages with Piped Water Connections", "positive") 

createmap("percent_hhd_mobilized_into_shg", "Percent HH mobilised into SHGs", "positive")

createmap("percent_shg_accessed_bank_loans", "Percent SHGs accessing bank loans", "positive")

#%%% Indicators, statwise, but only Aspirational Block means for each state. 

#now we want the same indicators as above, but for aspirational blocks only. 
#Hence, we use teh file created in block_analysis_MA, which takes means for all villages
#within all ABs within each state. 

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")

#created in block_analysis_MA
df = pd.read_csv("statelevel_abp.csv")
df = df[df.aspirational_block == 1] #keep state level averages for ABs. 

#read the shapefile and do the routine things. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/State GIS Files/Igismap")
statemap = gpd.read_file("Indian_States.shp")

statemap['st_nm'] = statemap['st_nm'].str.lower()

statemap.loc[statemap['st_nm'] == "andaman & nicobar island", 'st_nm'] = 'andaman and nicobar islands'
statemap.loc[statemap['st_nm'] == "arunanchal pradesh", "st_nm"] = "arunachal pradesh"
statemap.loc[statemap['st_nm'] == "dadara & nagar havelli", "st_nm"] = "dadra & nagar haveli and\ndaman & diu"

statemap = pd.merge(df, statemap, left_on = ['state_name'], right_on = ['st_nm'],
                    how = 'right')

statemap = gpd.GeoDataFrame(statemap, crs="EPSG:4326")

#create map: same as above. 
def createmap(varname, title, positive_or_negative):
    if positive_or_negative == "positive":
        cmap_color = "RdYlGn"
    elif positive_or_negative == "negative":
        cmap_color = "RdYlGn_r"
    statemap.plot(column = varname, cmap = cmap_color, legend = True,
                  missing_kwds= dict(color = "lightgrey"))
    plt.axis("off")
    plt.title('ABs: ' + title)
    os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")
    plt.savefig('ABs_' + title + "_statelevel.png", dpi = 1200)
 
#creating maps for only aspirational blocks. 
createmap("percent_anemic_pregnant_women", "Percent Anemic Pregnant Women", 
          "negative")

createmap("percent_underweight_child_age_under_6_years", "Percent Underweight children (below 6)", "negative")

createmap("availability_of_mid_day_meal_scheme_cleaned", "Percent Mid Day Meals Available" ,"positive")

createmap("is_pds_available_cleaned", "Percent PDS Shop Available in Village", "positive")

createmap("percent_hhd_not_having_sanitary_latrines", "Percent HH with no latrines", "negative")

createmap("availability_of_drainage_system_cleaned", "Percent Village with Any Drainage System" ,"positive")

createmap("percent_hhd_having_piped_water_connection", "Percent Villages with Piped Water Connections", "positive") 

createmap("percent_hhd_mobilized_into_shg", "Percent HH mobilised into SHGs", "positive")

createmap("percent_shg_accessed_bank_loans", "Percent SHGs accessing bank loans", "positive")

#%%% State Planning Secrataries:
    
#now we want the same indicators as above, but for aspirational blocks only. 
#Hence, we use teh file created in block_analysis_MA, which takes means for all villages
#within all ABs within each state. 

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files")

#created in block_analysis_MA
df = pd.read_csv("statelevel_abp.csv")
df = df[df.aspirational_block == 1] #keep state level averages for ABs. 

#read the shapefile and do the routine things. 
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/State GIS Files/Igismap")
statemap = gpd.read_file("Indian_States.shp")

statemap['st_nm'] = statemap['st_nm'].str.lower()

statemap.loc[statemap['st_nm'] == "andaman & nicobar island", 'st_nm'] = 'andaman and nicobar islands'
statemap.loc[statemap['st_nm'] == "arunanchal pradesh", "st_nm"] = "arunachal pradesh"
statemap.loc[statemap['st_nm'] == "dadara & nagar havelli", "st_nm"] = "dadra & nagar haveli and\ndaman & diu"

statemap = pd.merge(df, statemap, left_on = ['state_name'], right_on = ['st_nm'],
                    how = 'right')

statemap = gpd.GeoDataFrame(statemap, crs="EPSG:4326")

#create map: same as above. 
def createmap(varname, title, state, positive_or_negative):
    
    fig, axs = plt.subplots(figsize=(10, 10),
                        sharex=True,
                        sharey=True,
                        constrained_layout=True)
    
    if positive_or_negative == "positive":
        cmap_color = "RdYlGn"
    elif positive_or_negative == "negative":
        cmap_color = "RdYlGn_r"
    ax = statemap.plot(column = varname, cmap = cmap_color, legend = True,
                  missing_kwds= dict(color = "lightgrey"))
    statemap.loc[statemap.state_name == state].plot(ax = ax, facecolor='none', edgecolor='black', linewidth = 0.65)
    plt.axis("off")
    plt.title('ABs: ' + state.title() + ": "  + title)
    plt.figtext(0.5, 0.05, "National ABs Avg: " + str(df[df.state_name == 'india'][varname].mean()) + "\n" + state.title() + " ABs Avg: " + str(df[df.state_name == state][varname].mean()), ha="center",
                fontsize=12, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    plt.savefig(state+ "_" + title + "_statelevel.png", dpi = 1200)
   
os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/Planning Secretaries Viz Output Files")
#creating maps for only aspirational blocks. 
for state in statemap.state_name:
    if str(state) == "nan":
        continue
    
    createmap("percent_anemic_pregnant_women", "Percent Anemic Pregnant Women", 
              state,
              "negative")
    
    createmap("percent_underweight_child_age_under_6_years", "Percent Underweight children (below 6)",
              state, "negative")

    createmap("availability_of_mid_day_meal_scheme_cleaned", "Percent Mid Day Meals Available",
              state, "positive")

    createmap("is_pds_available_cleaned", "Percent PDS Shop Available in Village",
              state, "positive")

    createmap("percent_hhd_not_having_sanitary_latrines", "Percent HH with no latrines", state, "negative")

    createmap("availability_of_drainage_system_cleaned", "Percent Village with Any Drainage System",
              state, "positive")

    createmap("percent_hhd_having_piped_water_connection", "Percent Villages with Piped Water Connections",
              state, "positive") 

    createmap("percent_hhd_mobilized_into_shg", "Percent HH mobilised into SHGs",
              state, "positive")

    createmap("percent_shg_accessed_bank_loans", "Percent SHGs accessing bank loans",state,  "positive")

    print(state.title() + " over.")
    
#%%%


