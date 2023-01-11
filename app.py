from flask import Flask
app = Flask(__name__)
import logging
app.logger.setLevel(logging.INFO)

import flask
flask_version = flask.__version__
del flask

from flask import render_template, request, redirect, url_for, abort
import pandas as pd
import numpy as np
from pathlib import Path
from sys import version as python_version
from cat_graph_mpl import mpl_grapher
from cat_graph_px import cat_mapper, px_stats, px_spans
from cat_data import home_image, cat_data_save, cat_data_load, image_roto
from table_ops import spans_tables, words_tables, stats_tables, datas_tables, cat_page_table, cat_page_words, cat_map_table, comp_table
from api_v1 import api_catdata

# Create folders for graph files
Path(Path.cwd(),'static','graphs').mkdir(exist_ok=True)
Path(Path.cwd(),'static','plotly').mkdir(exist_ok=True)

# Load in data. Request, clean, and save if it doesn't exist.
data_path = (Path(Path.cwd(),'data'))
if(Path(data_path,'catdata.csv').exists()):
    data, statsCol, spansCol, binariesCol, wordsCol = cat_data_load(data_path)
else:
    app.logger.info('Loading Cat data . . . ')
    cat_data_save(data_path)
    data, statsCol, spansCol, binariesCol, wordsCol = cat_data_load(data_path)
del data_path

if app.debug == True: 
    app.logger.info('DEBUG MODE ENABLED')
    home_image = home_image('https://cdn2.thecatapi.com/images/OfIuuOv07.jpg') # start with image to minimize calls during development
else:
    home_image = home_image(None)

# create all MPL graphs at startup
app.logger.info('Prepopulating MPL graphs . . . ')
for cat in data.index[:-1]:
    _ = mpl_grapher(data, cat, data.index[-1], statsCol, spansCol, binariesCol)
    app.logger.info(f'\t{cat}')

app.logger.info('\nApplication Ready!')
@app.route("/")
@app.route("/home/")
def home(): # links and random cat image
    home_image.update()
    remaining = str(pd.Timedelta('10 min') - (pd.Timestamp.now() - home_image.stamp))[10:15]
    return render_template('home.html', home_image=home_image.image, remaining=remaining, flask_version=flask_version,
                           updated=home_image.stamp.round(freq='S'), python_version=python_version.split(' ')[0])

    
@app.route("/cats/")
def cat_index(): # list of cats+pic+description, links to data pages
    dataW = data.iloc[:-1,wordsCol.index] # extra words data
    return render_template('cat_index.html', dataW=dataW)


@app.route("/random/cat/")
def random_cat(): # random cat data page
    cat = pd.Series(data.index[:-1]).sample().values[0]
    return redirect(url_for('cat_page', cat=cat))

    
@app.route("/explore/api_info/")
def api_info(): # help page for API requests
    if not Path(Path.cwd(),'static','graphs','American Bobtail_spider-stats.jpg').exists(): # graph displayed on page
        _ = mpl_grapher(data, 'American Bobtail', data.index[-1], statsCol, spansCol, binariesCol)
    return render_template('api_info.html', home_image=home_image.image)

    
@app.route("/api/<req>")
def api_v1_basic(req): # image/name list API
    if req == 'image':
        home_image.update()
        return {'URL':home_image.image, 'minutes_left': str(pd.Timedelta('10 min') - (pd.Timestamp.now() - home_image.stamp))[10:15]}
    elif req == 'names':
        api_data = data.index[:-1]
        return {val:val.replace(' ','_').lower() for val in api_data}
    else:
        abort(400)


@app.route("/api/<cat>/<req>")
def api_v1_data(cat,req): # data for cat/random API
    cat = cat.replace('_',' ').title()
    if cat not in data.index[:-1] and cat != 'Random':
        abort(400)
    if cat == 'Random':
        cat = pd.Series(data.index[:-1]).sample().values[0]
    if req not in ['graph', 'info', 'stats']:
        abort(400)   
    api_data = api_catdata(cat, req, data, statsCol, spansCol, binariesCol, wordsCol)
    return api_data
        

@app.route("/compare", methods = ['GET','POST'])
def cat_compare(): # side-by-side comparison of two cats
    names = data.index.values[:-1] # list of cat names
    # return empties for GET method
    cat_one = cat_two = image_one = image_two = compW = compSpan = compStat = compBinary = ''
    if request.method == 'POST': # assemble data for tables
        cat_one = request.form['Cat One']
        cat_two = request.form['Cat Two']
        if not request.form.get('Cat Average'):
            comp_data = data.loc[(cat_one, cat_two),:]
        else:
            avg = data.index[-1]
            comp_data = data.loc[(cat_one, cat_two, avg),:]
        # Get formatted tables and images
        image_one, image_two, compW, compSpan, compStat, compBinary = comp_table(comp_data, statsCol, spansCol, binariesCol, wordsCol)  
    
    return render_template('cat_compare.html', names=names, cat_one=cat_one, cat_two=cat_two, image_one=image_one,
                           image_two=image_two, compW=compW, compSpan=compSpan, compStat=compStat, compBinary=compBinary)       


@app.route("/cats/<cat>")
def cat_page(cat): # data page for cat, all info+tables+graphs
    if cat not in data.index[:-1]:
        abort(404)
    avg_name = data.index[-1]
    graph_paths = mpl_grapher(data, cat, avg_name, statsCol, spansCol, binariesCol)    
    catW = data.loc[cat,wordsCol]
    AKA, cat_image, description, temperament, origin, wiki = cat_page_words(catW)   
    # Number data for Attributes section
    spans = data.loc[cat,spansCol]
    spans.index=['year lifespan','lb','kg'] # adjust for better display  
    binaries = data.loc[cat,binariesCol]
    binaries = binaries[binaries>0]
    binaries.index = [val.replace('_',' ') for val in binaries.index] # better display  
    # Cat data table
    cat_table = data.loc[[cat,avg_name],np.append(statsCol.values,np.append(spansCol.values, binariesCol.values))].transpose()
    cat_table = cat_page_table(cat_table, binariesCol, avg_name, cat)
    
    return render_template('cat_page.html', cat=cat, AKA=AKA, cat_image=cat_image, description=description, \
                           temperament=temperament, origin=origin, wiki=wiki, spans=spans, \
                           binaries=binaries, cat_table=cat_table, graph_paths=graph_paths)


@app.route("/graphs/map")
def map_cats(): # cat origins on Plotly world map
    cat_locs = data.loc[:,['origin','country_code']]
    cat_locs = cat_locs.iloc[:-1,:]
    map_table, locs = cat_map_table(cat_locs)    
    graphJSON = cat_mapper(cat_locs)
    return render_template('catmap.html', graphJSON=graphJSON, map_table=map_table)

      
@app.route("/graphs/map-raw")
def map_cats_raw(): # raw map file
    mapfile = Path(Path.cwd(),'static','plotly', 'cat_map.html')
    with open(mapfile, 'r') as reader:
        maphtml = reader.read()
    del reader
    return render_template('catmap_raw.html', maphtml=maphtml)
    
@app.route("/graphs/")
@app.route("/graphs/index")
def graphs_index(): # list of all generated graphs
    path = Path(Path.cwd(),'static','graphs')
    graphs = {}
    i = 1
    for child in path.iterdir():
        graphs[i] = child.name
        i = i+1
    return render_template('graphs_index.html', graphs=graphs)


@app.route("/data/")
@app.route("/data/story")
def data_story_index(): # links to data story
    return render_template('data_story_index.html')

@app.route("/data/background")
def background(): # resources, acknowledgements, data fetch
    return render_template('data_bg.html')
    
@app.route("/data/processing")
def processing(): # data cleaning and persistence
    return render_template('data_proc.html')

@app.route("/data/graphing")
def graphing(): # matplotlib and ploty graph examples
    return render_template('data_graph.html')
    
@app.route("/data/table")
def big_table(): # final table used for website
    names = data.index
    table = data.reset_index(drop=True) # Names to be replaced with links
    table.iloc[:-1,binariesCol.index] = table.iloc[:-1,binariesCol.index]  -1 # For easier replacement later  
    table.iloc[-1:, binariesCol.index] = table.iloc[-1:, binariesCol.index].apply(lambda val: f'{int(val*100)}%') # Format avg binaries as %
    
    table.index = [f'LINKONE{url_for("cat_page", cat=val, _external=True)}LINKTWO{val}LINKTHREE{val}LINKFOUR' for val in data.index] # Link structure, to be filled in
    table.rename(index={table.index[-1:][0]:names[-1:][0]}, inplace=True)   
    table = datas_tables(table)
    return render_template('data_table.html', table=table, names=names)


@app.route("/explore/")
@app.route("/explore/data")
def explore_data_index(): # links to data exploration
    return render_template('explore_data_index.html')
    
@app.route("/explore/stats")
def explore_stats(): # distributions of statistical data
    stats = data.iloc[:-1,statsCol.index]
    stats.columns = [val.replace('_',' ').title() for val in stats.columns]
    table, table2, meskew = stats_tables(stats)
    charts = px_stats(stats, meskew)
    return render_template('explore_stats.html', charts=charts, table=table, table2=table2) 
@app.route("/explore/words")

def explore_words(): # uniqueness of temperament descriptions
    dataW = data.iloc[:-1,wordsCol.index] # extra words data
    chart, table_ones, table_twos, table_mids, table_bigs, table_scores = words_tables(dataW)    
    
    return render_template('explore_words.html', table_ones=table_ones, table_twos=table_twos,
                           table_mids=table_mids, table_bigs=table_bigs, chart=chart, table_scores=table_scores)   

@app.route("/explore/spans", methods = ['GET','POST'])
def explore_spans(): # distribution of life spans, weight ranges
    spans = data.iloc[:-1,spansCol.index]
    spans, choices = spans_tables(spans)
    if request.method == 'GET':
        chart = name = bins = maxbins = ''
    else:
        name = request.form['colInput']
        bins = abs(int(request.form['binInput']))
        chart, maxbins = px_spans(spans, name, bins, choices)   
        if bins == 0:
            bins = 'auto'
    return render_template('explore_spans.html', choices=choices, chart=chart,
                           name=name, bins=bins, maxbins=maxbins)
      
@app.route("/favicon.ico")
def favicon(): # leaving in for fun
    image = "favicon.ico"
    return render_template('image.html', image=image)     