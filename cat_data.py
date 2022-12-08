from pathlib import Path
import requests as re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import json

def image_roto(stamp, image):   
    delta = pd.Timestamp.now() - stamp
    if delta > pd.Timedelta('10 min') or image == None:
        try:
            image = re.get("https://api.thecatapi.com/v1/images/search").json()[0]['url']
        except: # null return from thecatapi.com, could do a sleep / retry
            pass
        stamp = pd.Timestamp.now()
    return stamp, image

class home_image:
    def __init__(self, start):
        self.stamp = pd.Timestamp.now()
        self.image = start # None for deployment, start with cat image for DEBUG to minimize calls
        self.update()
    def update(self):
        stamp, image = image_roto(self.stamp, self.image)
        self.stamp = stamp
        self.image = image

def cat_data_save(data_path):
    cat = pd.DataFrame(re.get("https://api.thecatapi.com/v1/breeds").json()) # import data as JSON file
    
    # drop data
    # urls mostly empty, id is abbreviated name, ref image ID n/a
    # country_codes is repeat of country_code, others low spread or mostly empty
    cat.drop(columns = ['id','cfa_url','vetstreet_url','vcahospitals_url','reference_image_id',\
                        'lap','cat_friendly','bidability', 'country_codes'],\
             inplace = True)

    # Extract weight into two columns from imperial/metric dictionary entry
    # delete original, could convert to ints and have min/max columns
    for i,val in enumerate(cat.weight):
        cat.loc[i,'weight_lb'] = val['imperial']
        cat.loc[i,'weight_kg'] = val['metric']
    cat.drop(columns = 'weight', inplace = True)  

    # Extract only the image URL from the image info dictionary
    for i,val in enumerate(cat.image):
        if type(val) == dict and 'url' in val:
            cat.loc[i,'image'] = val['url']
        else:
            cat.loc[i,'image'] = ''
        
    # Add wikipedia link to burmese cat, only one missing
    ind = cat[cat.wikipedia_url.isnull()].index
    cat.loc[ind,'wikipedia_url'] = 'https://en.wikipedia.org/wiki/Burmese_cat'
    del ind

    # Find Image from wikipedia page and add to image-less cats
    for i,val in enumerate(cat[cat.image == ''].index):
        URL = cat.loc[val,'wikipedia_url']
        page = re.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        all_links = soup.find_all('a',class_= 'image')
        if str([all_links[0]]).find('Question_book-new.svg') == -1: # One page has a question book icon (Asian_cat)
            link_info = str(all_links[0])
        else:
            link_info = str(all_links[1])
        fat = link_info[link_info.find('src='):link_info.find('srcset=')]
        
        if fat.find('.jpg') == -1: # Some extensions are written as .JPG instead of .jpg
            extension = '.JPG'
        else:
            extension = '.jpg'
            
        base = fat[fat.find('/thumb'.lower())+6:fat.find(extension)+4]
        image_link = f'https://upload.wikimedia.org/wikipedia/commons{base}'
        # print(image_link) # Check image link works
        cat.loc[val,'image'] = image_link
    
    # Fill empty values + special characters in alt names, helps future indexing
    cat.alt_names.fillna('',inplace=True)
    cat.alt_names.replace(to_replace = '\xa0', value = '', inplace = True)
    
    # Adjust country_code from alpha-2 to 3
    codes = pd.read_csv(Path(data_path, 'countries.csv'), index_col = 'Country')
    for val in cat.index:
        CC = cat.loc[val,'country_code']
        try:
            ind = codes[codes['Alpha-2 code'] == CC].index[0]
            cat.loc[val,'country_code'] = codes.loc[ind,'Alpha-3 code'].replace('"','').replace(' ','') # values have junk characters
        except:
            try: # Singapore alpha 2 code is different, note Iran full name is dfferent on the data frames
                country = cat.loc[val,'origin']
                cat.loc[val,'country_code'] = codes.loc[country,'Alpha-3 code'].replace('"','').replace(' ','')
            except:
                pass
            pass
        
    # Determine column data types:
    # Seperate by strings (words: various descriptions, ranges (spans: 'x - y', integers (stats: 0-5), and binary (binaries: 0-1) data
    # Add averages as applicable
    cat.set_index('name', inplace = True)
    stats = pd.Series(dtype=int)
    words = pd.Series(dtype=object)
    binaries = pd.Series(dtype=int)
    spans = pd.Series(dtype=int)

    for i,val in enumerate(cat.columns): # Exclude Name, which is the key for index
        if cat[val].dtype == 'object':
            if cat[val][0].replace(' ', '').replace('-','').isdigit(): # Check for "<integer> - <integer>" format, leave spans as strings
                spans.loc[i] = val
                cat.loc['CatAPI Average',val] = ''
                cat[val] = cat[val].apply(lambda span_string: span_string.replace(' ',''))

                lower = []
                upper = []
                for j, cal in enumerate(cat[val][:-1]):
                    values = cal.split('-')
                    lower.append(float(values[0]))
                    upper.append(float(values[1]))
                lower_avg = round(np.mean(lower),1)
                upper_avg = round(np.mean(upper),1)
                cat.loc['CatAPI Average',val] = f'{lower_avg}-{upper_avg}'

            else:
                words.loc[i] = val # letterly descriptions
                # No average for words

        else: # only other datatype is int64, could specify here
            if np.min(cat[val]) == 0:
                binaries.loc[i] = val # binary stats are 0 or 1
                avg = round(np.mean(cat[val]),2)
                cat.loc['CatAPI Average',val] = avg
            else:
                stats.loc[i] = val # other stats are 1-5
                avg = round(np.mean(cat[val]),2)
                cat.loc['CatAPI Average',val] = avg
                
    # Save to CSVs
    cat.to_csv(Path(data_path, 'catdata.csv'))
    stats.to_csv(Path(data_path, 'stats.csv'))
    words.to_csv(Path(data_path, 'words.csv'))
    binaries.to_csv(Path(data_path, 'binaries.csv'))
    spans.to_csv(Path(data_path, 'spans.csv'))

def cat_data_load(data_path):
    # Read CSVs and return pandas objects
    data = pd.read_csv(Path(data_path,'catdata.csv'), index_col = 'name', na_filter = False)
    statsCol = pd.Series(pd.read_csv(Path(data_path, 'stats.csv'), index_col = 0)['0'], name = 'Cols')
    spansCol = pd.Series(pd.read_csv(Path(data_path,'spans.csv'), index_col = 0)['0'], name = 'Cols')
    binariesCol = pd.Series(pd.read_csv(Path(data_path,'binaries.csv'), index_col = 0)['0'], name = 'Cols')
    wordsCol = pd.Series(pd.read_csv(Path(data_path,'words.csv'), index_col = 0)['0'], name = 'Cols')
    return data, statsCol, spansCol, binariesCol, wordsCol