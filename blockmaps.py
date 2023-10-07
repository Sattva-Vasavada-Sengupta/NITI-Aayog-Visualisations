import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import geopandas as gpd
import seaborn as sns
import matplotlib.style as style 

from functools import reduce

#%%

#define function to convert list to string
def listToString(s):
 
    str1 = ""
 
    for ele in s:
        str1 = str1 + " " + ele
 
    # return string
    return str1.strip()


#%% Read block shapefiles

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Block GIS Files")
blockmap = gpd.read_file("Block_boundary.shp")
blockmap.columns = blockmap.columns.str.lower() #column names to lowercase. 

#%% Read datafile

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Latest Data Files")
edu = pd.read_excel("ABP_Baseline Education_New.xlsx", sheet_name = 'baseline_withoutvlookup')

#change column names 
edu.columns = ['S.NO.', 'statename_edu', 'statecode_edu', 'districtname_edu', 'districtcode_edu', 
               'blockname_edu', 'blockcode_edu',
       'Transition Rate - Percentage of boys transitioned from Upper Primary to Secondary level',
       'Transition Rate - Percentage of girls transitioned from Upper Primary to Secondary level',
       'Transition Rate - Percentage of boys transitioned from Secondary to Higher Secondary Level',
       'Transition Rate - Percentage of girls transitioned from Secondary to Higher Secondary Level',
       'Percentage of elementary schools having PTR less than equal to 30',
       'Percentage of schools having adequate no. of girls’ toilet facilities against the total number of schools',
       'Percentage of schools having trained teachers for teaching child with special needs (CwSN)',
       'Percentage of boys with 60% and above marks in Class X board exam',
       'Percentage of girls with 60% and above marks in Class X board exam',
       'Percentage of boys with 60% and above marks in Class XII board exam',
       'Percentage of girls with 60% and above marks in Class XII board exam']

#replace 0* with np.nan 
edu.replace("0*", 0, inplace = True)

#merge with blockmap
edumap = pd.merge(edu, blockmap, left_on = ['blockcode_edu'], 
                  right_on = ['block_lgd'], how = 'outer')

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/data/Latest Data Files/Data Validation")
edumap.drop('geometry', axis = 1)[edumap.block_name.isna() == True].to_excel("edu_blockmap no merge.xlsx")

test = edumap.drop(['geometry'], axis = 1 )

#%% Map stuff now

edumap = gpd.GeoDataFrame(edumap)

collist = ['Transition Rate - Percentage of boys transitioned from Upper Primary to Secondary level',
'Transition Rate - Percentage of girls transitioned from Upper Primary to Secondary level',
'Transition Rate - Percentage of boys transitioned from Secondary to Higher Secondary Level',
'Transition Rate - Percentage of girls transitioned from Secondary to Higher Secondary Level',
'Percentage of elementary schools having PTR less than equal to 30',
'Percentage of schools having adequate no. of girls’ toilet facilities against the total number of schools',
'Percentage of schools having trained teachers for teaching child with special needs (CwSN)',
'Percentage of boys with 60% and above marks in Class X board exam',
'Percentage of girls with 60% and above marks in Class X board exam',
'Percentage of boys with 60% and above marks in Class XII board exam',
'Percentage of girls with 60% and above marks in Class XII board exam']

os.chdir("D:/Users/savas/Documents/Ashoka/Economics/NITI Aayog/Aspirational Blocks Program/Block Analysis/output files/Latest Data Output/Education")
for col in collist:
    ax = edumap.plot(column = col,  cmap='RdYlGn', legend = True, missing_kwds = dict(color = "lightgrey"))
    edumap.loc[(edumap.blockcode_edu.isna() == False)].plot(ax = ax, facecolor='none', edgecolor='black', linewidth = 0.3, alpha = 0.5)
    
    abavg = np.round(np.mean(edumap[col]), 1)
    
    plt.figtext(0.5, 0.05, "Aspirational Block Average: " + str(abavg), ha="center",
                fontsize=12, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    
    plt.axis('off')
    
    plot_title = col.split(" ")
    plot_title.insert(int(np.round(len(plot_title)/2, 0)), '\n')

    plot_title = listToString(plot_title)
    
    plt.title(plot_title)
    plt.savefig(col + ".png", dpi = 1200, bbox_inches='tight')
    plt.close()
    print("Over:", col)

#%% 
