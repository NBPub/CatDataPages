from pathlib import Path
import pandas as pd
import numpy as np
from cat_graph_px import px_words

def comp_table(comp_data, statsCol, spansCol, binariesCol, wordsCol):
    compW = comp_data.loc[:, wordsCol]
    if 'CatAPI Average' in comp_data.index:
        compW.drop('CatAPI Average', inplace=True)
    image_one = compW.image[0]
    image_two = compW.image[1]
    compW.drop(columns = ['country_code', 'image'], inplace=True)
    compW.columns = [val.replace('_',' ').capitalize() for val in compW.columns]
    compW = compW.transpose().to_html(justify = 'left', index_names = False, render_links = True)
    compW = compW.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    
    compSpan = comp_data.loc[:,spansCol].transpose().to_html(justify = 'left', index_names = False)
    compSpan = compSpan.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    
    compStat = comp_data.loc[:,statsCol]
    compStat.columns = [val.replace('_',' ').title() for val in compStat.columns]
    compStat = compStat.transpose().convert_dtypes().to_html(justify = 'left', index_names = False)
    compStat = compStat.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    
    compBinary = comp_data.loc[:,binariesCol].transpose() 
    compBinary.index = [val.replace('_',' ').title() for val in compBinary.index]
    if 'CatAPI Average' in compBinary.columns:
        compBinary['CatAPI Average'] = compBinary['CatAPI Average'].apply(lambda val: f'{int(val*100)}%')

    compBinary = compBinary.to_html(justify = 'left', index_names = False)
    compBinary = compBinary.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    compBinary = compBinary.replace('0.0','&#10060;')
    compBinary = compBinary.replace('1.0','&#10004;')
    
    return image_one,image_two, compW, compSpan, compStat, compBinary


def cat_map_table(cat_locs):
    # Prepare table
    locs = pd.DataFrame(cat_locs.value_counts()).reset_index() # organize by number of cats from country
    locs.columns = (['origin','code','# cats']) # rename columns    
    locs['cats'] = [', '.join(cat_locs[cat_locs.origin == val].index) for val in locs['origin']] # Get cats belonging to country
    
    map_table = locs.set_index('origin')
    map_table.drop(columns = ['code'], inplace=True)
    map_table = map_table.to_html(justify = 'left', index_names = False)
    map_table = map_table.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    return map_table, locs  

def cat_page_words(catW):
    AKA = catW['alt_names'].split(',')
    cat_image = catW['image']
    description = catW['description']
    temperament = catW['temperament']
    origin = f'{catW["origin"]} ({catW["country_code"]})'
    wiki = catW['wikipedia_url']
    return AKA, cat_image, description, temperament, origin, wiki

def cat_page_table(cat_table, binariesCol, avg_name, cat):
    cat_table.loc[binariesCol,cat] = cat_table.loc[binariesCol,cat] -1
    cat_table.loc[binariesCol,avg_name] = cat_table.loc[binariesCol,avg_name].apply(lambda val: f'{int(val*100)}%')
    cat_table.index = [val.replace('_',' ').title() for val in cat_table.index]
    cat_table = cat_table.to_html(justify='left', index_names=False)
    
    # Add bootstrap
    cat_table = cat_table.replace("dataframe", "table table-dark table-striped table-hover ms-2") 
    cat_table = cat_table.replace('<thead>','<thead class="sticky-top" style="top: 55px">') # sticky column labels to scroll below navbar
    # Manually adjust values for formatting
    cat_table = cat_table.replace('-1.0','&#10060;')
    cat_table = cat_table.replace('0.0','&#10004;')
    cat_table = cat_table.replace('.0','')    
    return cat_table

def datas_tables(table):  
    table = table.to_html(justify='left', index_names=False, show_dimensions=True, render_links=True)
    table = table.replace("dataframe", "table table-dark table-striped table-hover ms-2") # bootstrap styling
    table = table.replace('<thead>','<thead class="sticky-top" style="top: 55px">') # sticky column labels to scroll below navbar
    
    # Fill in links for index
    table = table.replace('LINKONE','<a href="') # sticky column labels to scroll below navbar
    table = table.replace('LINKTWO','" id="') # sticky column labels to scroll below navbar
    table = table.replace('LINKTHREE','">') # sticky column labels to scroll below navbar
    table = table.replace('LINKFOUR','</a>') # sticky column labels to scroll below navbar
    table = table.replace('<th>CatAPI Average</th>','<th id="CatAPI Average">CatAPI Average</th>') # specfic link for Cat API Average
    
    # Manually adjust values for formatting
    table = table.replace('-1.0','&#10060;')
    table = table.replace('0.0','&#10004;')
    table = table.replace('.00','')
    return table

def stats_tables(stats):
    table = stats.describe().iloc[[0,1,2,3,7],:].transpose() # don't take quartiles
    table['count'] = table['count'].astype('int')
    table['mean'] = table['mean'].round(1)
    table['std'] = table['std'].round(1)
    table['min'] = table['min'].astype('int')
    table['max'] = table['max'].astype('int')
    
    table2 = pd.DataFrame(columns = [1,2,3,4,5,' ', 'meskew'])
    for col in stats.columns:
        counts = stats[col].value_counts()
        total = 0
        for val in counts.index:
            table2.loc[col,val] = counts.loc[val]
            total += val*counts.loc[val]
        table2.loc[col,'meskew'] = (round(total / (67*3),1)-1)*-1
    table2.loc[:,' '] = ' '
    table2.fillna(0, inplace=True)
    meskew = dict(round(table2.meskew,1))
    
    table = table.to_html(justify='left', index_names=False, show_dimensions=True)
    table = table.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    table2 = table2.to_html(justify='left', index_names=False, show_dimensions=True)
    table2 = table2.replace("dataframe", "table table-dark table-striped table-hover ms-2")    
    return table, table2, meskew
    
def spans_tables(spans):
    spans['life_span'] = [np.mean([int(val.split('-')[0]), int(val.split('-')[1])]) for val in spans['life_span']]
    spans['weight_lb'] = [np.mean([int(val.split('-')[0]), int(val.split('-')[1])]) for val in spans['weight_lb']]
    spans['weight_kg'] = [np.mean([int(val.split('-')[0]), int(val.split('-')[1])]) for val in spans['weight_kg']]
    spans.columns = [val.replace('_',' ').capitalize() for val in spans.columns]
    
    choices = {}
    for val in spans.columns:
        choices[val] = spans[val].unique().shape[0]
    return spans, choices

def words_tables(dataW):
    # CONSIDER SAVING THIS ONE
    words = [] # List of all the words used in Temperament
    catlist = {} # List of Temperament words for each cat,  used for ones and table_twos
    for val in dataW.index:
        temperament = dataW.loc[val,'temperament']  
        for word in temperament.split(','):
            nicer_word = word.replace(' ','').capitalize()
            words.append(nicer_word)
            if nicer_word in catlist:
                catlist[nicer_word] = ', '.join([catlist[nicer_word],val])
            else:
                catlist[nicer_word] = val
        
    wordcount = pd.DataFrame(pd.Series(words).value_counts(), columns = ['cats'])
    chart = px_words(wordcount)
    
    # tables
    table_bigs = wordcount[wordcount.cats > 9] # 10 or greater
    table_mids = wordcount[(wordcount.cats > 2) & (wordcount.cats < 10)] # from 3 to 9
    
    # tables with additions
    table_twos = wordcount[wordcount.cats == 2]
    for val in table_twos.index:
        table_twos.loc[val,'cat'] = catlist[val]
    
    table_ones = wordcount[wordcount.cats == 1]
    for val in table_ones.index:
        table_ones.loc[val,'cat'] = catlist[val]
    
    # Score cats on rarity of temperament words
    table_scores = pd.DataFrame(dataW['temperament'])
    for val in table_scores.index:
        temps = table_scores.loc[val,'temperament'].split(', ')
        score = 0
        for word in temps:
            score += wordcount.loc[word.replace(' ','').capitalize(),'cats']
        table_scores.loc[val,'score'] = score
        table_scores.loc[val,'words'] = len(temps)
    
    table_scores['score/words'] = table_scores['score'] / table_scores['words'] 
    table_scores.drop(columns = ['words'], inplace=True)
    
    table_scores['score/words'] = round(table_scores['score/words'],1)
    table_scores['score'] = table_scores['score'].astype(int)
    
    # to html and add bootstrap classes for CSS
    table_ones = table_ones.to_html(justify='center', index_names=False, show_dimensions=True)
    table_ones = table_ones.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    
    table_twos = table_twos.to_html(justify='center', index_names=False, show_dimensions=True)
    table_twos = table_twos.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    
    table_mids = table_mids.to_html(justify='center', index_names=False, show_dimensions=True)
    table_mids = table_mids.replace("dataframe", "table table-dark table-striped table-hover ms-2")
    
    table_bigs = table_bigs.to_html(justify='center', index_names=False, show_dimensions=True) 
    table_bigs = table_bigs.replace("dataframe", "table table-dark table-striped table-hover ms-2")

    table_scores = table_scores.sort_values(by='score/words').to_html(justify='center', index_names=False)
    table_scores = table_scores.replace("dataframe", "table table-dark table-striped table-hover ms-2")
                
    return chart, table_ones, table_twos, table_mids, table_bigs, table_scores