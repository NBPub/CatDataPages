from pathlib import Path
import pandas as pd
import plotly.utils as pu
import plotly.express as px
import json
    
def cat_mapper(locs):
    
    # if file for map exists, don't need to make again
    path = Path(Path.cwd(),'static','plotly', 'cat_map.json')
    if path.exists():
        with open(path, 'r') as reader:
            graphJSON = reader.read()
        del reader
        return graphJSON    
    
    # Gather country cat count, list of cats
    mapdata = pd.DataFrame(locs.value_counts()).reset_index()
    mapdata.columns = (['origin','code','# cats'])
    mapdata['cats'] = [', '.join(locs[locs.origin == val].index) for val in mapdata['origin']] # Get cats belonging to country
    mapdata['origin'] = [f'{mapdata.loc[val,"origin"]} ({mapdata.loc[val,"# cats"]})' for val in mapdata.index] # Add (# cats) for display      
    mapdata.set_index('origin', inplace=True)  
    
    fig = px.choropleth(mapdata, locations="code", color="# cats", hover_name=mapdata.index,
                        hover_data = {'code': False, '# cats': False, 'cats': True,},
                        color_continuous_scale=px.colors.sequential.Emrld)

    fig.update_geos(showcountries = True, coastlinewidth = 1.5, landcolor = '#dedede', lakecolor = '#b0ceff', showocean = True, oceancolor = '#b0ceff',
                    showrivers = True, rivercolor = '#b0ceff', projection_type = 'natural earth', fitbounds = "locations")
    
    fig.write_html(Path(Path.cwd(),'static','plotly', 'cat_map.html'))
    
    graphJSON = json.dumps(fig, cls=pu.PlotlyJSONEncoder)
    with open(path, 'w') as writer:
        writer.write(graphJSON)
    del writer
    
    return graphJSON
    
    
def px_stats(stats, meskew):    
    # if file exists, split lines into dictionary and return
    path = Path(Path.cwd(),'static','plotly', 'cat_stats_JSONs.txt')
    if path.exists():
        with open(path, 'r') as reader:
            graphJSONs = reader.read()
        del reader
        graphJSONs = graphJSONs.split('\n')
        
        charts = {}
        for i,line in enumerate(graphJSONs):
            charts[stats.columns[i]] = line  
        return charts
    
    # else, extract stats, make graphs, save data as JSON lines
    graphJSONs = []
    for i,val in enumerate(stats.columns):
        fig = px.histogram(stats, x=val,  marginal="box", color_discrete_sequence = px.colors.qualitative.Prism)
        fig.update_xaxes(range=[0.5,5.5])
        fig.update_layout(bargap=0.2, title={'text': f'{val} | meskew:{meskew[val]}', 'font_color':'#362073', 'x':0.5, 'y':0.9},
                          xaxis_title_text='Value', yaxis_title_text='Number of Cats', plot_bgcolor="#e8d887",
                          hoverlabel = dict(bgcolor = 'white', font_size= 14, font_family = 'Rockwell'))
    
        graphJSONs.append(json.dumps(fig, cls=pu.PlotlyJSONEncoder))
    
    # Send chart data as dictionary
    charts = {}
    for i,line in enumerate(graphJSONs):
        charts[stats.columns[i]] = line  
    
    graphJSONs = '\n'.join(graphJSONs)
    # Write to file
    with open(path, 'w') as writer:
        writer.writelines(graphJSONs)
    del writer
   
    return charts
    
def px_words(wordcount):
    fig = px.histogram(wordcount, x="cats",  marginal="violin", nbins=22)

    fig.update_layout(bargap=0.2, title={'text': "Words Describing Cat Temperament", 'font_color':'#362073', 'x':0.5, 'y':0.9},
                      xaxis_title_text='Cats described by Word', yaxis_title_text='Number of Words in bin', plot_bgcolor="#e8d887",
                      hoverlabel = dict(bgcolor = 'white', font_size= 14, font_family = 'Rockwell'))
    chart = json.dumps(fig, cls=pu.PlotlyJSONEncoder)
    return chart
    
def px_spans(spans, name, bins, choices):
    maxbins = choices[name]
    fig = px.histogram(spans, x=name,  marginal="violin", nbins=bins)
    fig.update_layout(bargap=0.2, title={'text': f'{name} distribution', 'font_color':'#362073', 'x':0.5, 'y':0.9},
                      xaxis_title_text=f'average {name} range', yaxis_title_text='Number of Cats', plot_bgcolor="#e8d887",
                      hoverlabel = dict(bgcolor = 'white', font_size= 14, font_family = 'Rockwell'))
    chart = json.dumps(fig, cls=pu.PlotlyJSONEncoder)
     
    return chart, maxbins