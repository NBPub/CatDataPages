from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def spider(statsTable, avg_name, n_cats):
    cat = statsTable.index[0]
    path = Path(Path.cwd(),'static','graphs', f'{cat}_spider-stats.jpg')
    graph_path = f'graphs/{cat}_spider-stats.jpg'
    # if exists, don't make again
    if path.exists():
        return graph_path
    
    stats = statsTable.iloc[0,:]
    avg_stats = statsTable.iloc[1,:]
    # angles for each category, reduce amount of categories if it looks cluttered
    # calculates position/portion of perimeter (2*pi*r, where r = 1) for each category
    angles = [x / avg_stats.shape[0] * 2 * np.pi for x in range(avg_stats.shape[0])]
    angles2 = np.append(angles, angles[0]) # repeat first value to close circle 
    
    # theta values for cat and avg stats, again repeat first value to close circle
    catY = np.append(stats.values,(stats[0]))
    avgY = np.append(avg_stats.values,(avg_stats[0]))
    
    labeler = [val.replace('_',' ').capitalize() for val in stats.index.values]
    avg_text = f'{avg_name} (n={n_cats})'
    
    # Plot and save
    plt.figure(figsize = (8,7), dpi = 150, tight_layout=True)
    ax = plt.subplot(111, polar = "True")
    ax.spines['polar'].set_visible(False)
    plt.ylim(0,6) # extend lines past 5

    # plot sample data over mean as background
    plt.fill(angles2,catY,alpha = 0.25, color = 'cyan', ec ='darkcyan', linewidth = 2, linestyle ='-') # Cat fill
    plt.fill(angles2,avgY,alpha = 0.20, color = 'coral', ec='orangered') # Avg background fill

    # ticks
    plt.xticks(angles,labeler, fontweight = 'bold' ) # add attribute labels at their position
    plt.yticks([1,2,3,4,5], fontsize=0) # provide theta lines for 1-5
    for num in [1,3,5]:
        plt.text(np.pi*5/12, num, num, fontsize = 12, fontweight='bold') # only label 1,3,5
        
    # sample stat labels
    bbox_props = dict(boxstyle="circle, pad = 0.22", fc="cyan", ec="darkcyan", lw=2)
    for i,val in enumerate(stats):
        ax.text(angles[i], int(val), str(int(val)), color = 'black', fontweight = 'bold', bbox=bbox_props)

    # title / legend
    plt.title(stats.name, loc='left', fontsize=18, fontweight='bold', color = 'darkcyan')
    plt.text(3*np.pi/4,8.8, avg_text, fontsize = 12, fontweight = 'bold', color = 'orangered')
    
    # save
    
    plt.savefig(path)
    plt.close()
    return graph_path
    
def binary(binariesTable, avg_name, n_cats):
    cat = binariesTable.index[0]
    path = Path(Path.cwd(),'static','graphs', f'{cat}_binaries.jpg')
    graph_path = f'graphs/{cat}_binaries.jpg'
    # if exists, don't make again
    if path.exists():
        return graph_path
    
    plt.figure(figsize = (6,3), dpi = 150, tight_layout=True)
    for i,val in enumerate(binariesTable.columns):
        plt.subplot(331+i)
        if i == 1:
            plt.title(f'{cat} Binary Attributes', color = 'darkcyan', fontweight = 'bold', wrap = True)
        if i == 2:
            plt.text(0.8, 0.15, f'CatAPI Avg [{n_cats}]', fontsize=9, color = 'darkorange', fontweight = 'bold', ha = 'center')
        catX = binariesTable.loc[cat,val]
        avgX = binariesTable.loc[binariesTable.index[1],val]
        plt.plot(catX,0.01,marker = 'o', color = 'darkcyan', markersize = 20, alpha = 0.3) # bubble for cat
        plt.plot(avgX, 0, marker = 'd', color = 'darkorange', markersize = 14)
        plt.plot([0,1],[0,0], 'k-')
        plt.axis([-0.1, 1.1, -0.1, 0.1])
        
        if catX == 0:
            plt.text(0.5, 0.02, val.replace('_',' ').capitalize(), ha = 'center', color = 'grey') # attribute label for no's
        else:
            plt.text(0.5, 0.02, val.replace('_',' ').capitalize(), ha = 'center', fontweight = 'bold', color='darkcyan') # attribute label for yes's
        
        plt.text(0.0, 0, 'no', ha = 'center', color = 'black') # 0 label
        plt.text(1.0, 0, 'yes', ha = 'center', color = 'black') # 1 label
        plt.text(avgX+0.03, -0.05, f'{int(100*avgX)}%', ha = 'left', color = 'darkorange', fontweight = 'bold') # 1 avg marker
        
        plt.axis('off')
    # save
    plt.savefig(path)
    plt.close()  
    return graph_path

def ranger(spansTable, avg_name, n_cats):
    cat = spansTable.index[0]
    path = Path(Path.cwd(),'static','graphs', f'{cat}_ranges.jpg')
    graph_path = f'graphs/{cat}_ranges.jpg'
    # if exists, don't make again
    if path.exists():
        return graph_path
        
    spansTable.columns=['Lifespan (years)','weight (lb)','weight (kg)'] # adjust for better display

    plt.figure(figsize = (3,5), dpi = 150, tight_layout=True)
    for i,val in enumerate(spansTable.columns):
        ax = plt.subplot(311+i)
        if i == 0:
            plt.title(f'{cat} Span Data', color = 'darkcyan', fontweight = 'bold', wrap = True)
        catMin = int(spansTable.loc[cat,val].split('-')[0])
        catMax = int(spansTable.loc[cat,val].split('-')[1])
        avgMin = float(spansTable.loc[avg_name,val].split('-')[0])
        avgMax = float(spansTable.loc[avg_name,val].split('-')[1])
        
        plt.plot([catMin,catMax],[-0.03,-0.03], 'o-', linewidth = 3, markersize = 12, color = 'darkcyan') # bubble for cat
        plt.plot([catMin,catMin], [-0.1,-0.03], '--', color = 'darkcyan', alpha = 0.5)
        plt.plot([catMax,catMax], [-0.1,-0.03], '--', color = 'darkcyan', alpha = 0.5)

        plt.plot([avgMin,avgMax],[0,0], 'o-', linewidth = 3, markersize = 12, color = 'darkorange') # bubble for cat
        plt.plot([avgMin,avgMin], [-0.1,0], '--', color = 'darkorange', alpha = 0.5)
        plt.plot([avgMax,avgMax], [-0.1,0], '--', color = 'darkorange', alpha = 0.5)
        
        mini = np.min([catMin,avgMin])
        maxi = np.max([catMax,avgMax])
        plt.axis([mini-1, maxi+1, -0.1, 0.1])
        plt.text(np.mean([catMin,catMax]), -0.07, val.replace('_',' ').capitalize(), ha = 'center', color = 'darkcyan') # plot label
        plt.text(np.mean([avgMin,avgMax]), 0.01, f'CatAPI Avg [{n_cats}]', ha = 'center', color = 'darkorange', fontsize = 9) # plot label
        
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        plt.yticks([])

    # save
    plt.savefig(path)
    plt.close()
    return graph_path

def mpl_grapher(data, cat, avg_name, statsCol, spansCol, binariesCol):
    n_cats = data.shape[0]-1
    statsTable = data.loc[[cat,avg_name],statsCol] 
    spansTable = data.loc[[cat,avg_name],spansCol]
    binariesTable = data.loc[[cat,avg_name],binariesCol]
    del data
    
    path1 = spider(statsTable, avg_name, n_cats)
    path2 = binary(binariesTable, avg_name, n_cats)
    path3 = ranger(spansTable, avg_name, n_cats)
    graph_paths = {'spider': path1, 'binaries': path2, 'ranges': path3}
    return graph_paths
    
    
