from flask import url_for
from table_ops import cat_page_words
from cat_graph_mpl import mpl_grapher
 
def api_catdata(cat,req,data, statsCol, spansCol, binariesCol, wordsCol):
    if req == 'graph':
        graph_paths = mpl_grapher(data, cat, data.index[-1], statsCol, spansCol, binariesCol)
        for key,val in graph_paths.items():
            graph_paths[key] = url_for('static', filename=val, _external=True)
        graph_paths.update({'Cat':cat, 'Data':'graph URLs', 'Page':url_for('cat_page', cat=cat, _external=True)})
        return graph_paths
    elif req == 'info':
        catW = data.loc[cat,wordsCol]
        AKA, cat_image, description, temperament, origin, wiki = cat_page_words(catW)
        binaries = data.loc[cat,binariesCol]
        binaries = binaries[binaries>0]
        binaries = [val.replace('_',' ') for val in binaries.index]      
        info = {'Cat':cat, 'Data':'information', 'Page': url_for('cat_page', cat=cat, _external=True),
            'description':description, 'temperament':temperament, 'traits':binaries, 'origin':origin, 
            'alt names':AKA, 'image':cat_image, 'wikipedia':wiki}
        return info        
    elif req == 'stats':
        stats = {'Cat':cat, 'Data':'stats', 'Page': url_for('cat_page', cat=cat, _external=True)}
        stats.update(data.loc[cat,spansCol].to_dict())
        stats.update(data.loc[cat,statsCol].to_dict())
        return stats
    else:
        return {}