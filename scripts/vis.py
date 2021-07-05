from fa2 import ForceAtlas2
from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import json

def parse_net_components(rtedgelistfp, htedgelistfp, figfp=None, figtitle='Distribution of connected component sizes', v=True):
    rt_g = nx.read_weighted_edgelist(rtedgelistfp)
    rt_connected = [len(c) for c in sorted(nx.connected_components(rt_g), key=len, reverse=True)]
    rt_largest_cc = max(nx.connected_components(rt_g), key=len)
    rt_h = deepcopy(rt_g.subgraph(rt_largest_cc))

    ht_g = nx.read_weighted_edgelist(htedgelistfp)
    ht_connected = [len(c) for c in sorted(nx.connected_components(ht_g), key=len, reverse=True)]
    ht_largest_cc = max(nx.connected_components(ht_g), key=len)
    ht_h = deepcopy(ht_g.subgraph(ht_largest_cc))

    sns.set_theme(style='whitegrid', font_scale=.5)
    fig = plt.figure(figsize=(6,8))
    fig.suptitle(figtitle)
    axs = fig.subplots(1,2, sharey=False)
    params = dict(color='navy', alpha=.82, log=True)
    for ax, title, ylab, connected in zip(axs, ('Retweet network', 'Hashtag network'), ('component size', ''), (rt_connected, ht_connected)):
        sns.countplot(y=connected, ax=ax, **params)
        ax.set(title=title, ylabel=ylab, xlabel='occurances')
    #fig.tight_layout()

    try:
        fig.savefig(figfp)
        print('Figure {} saved to {}'. format(figtitle, figfp))
    except Exception as e:
        print(e)

    return dict(rt_g=rt_g, rt_h=rt_h, ht_g=ht_g, ht_h=ht_h)



def vis_net_stats(edgelistfp, figfp=None, title='', v=False):
    
    g = nx.read_weighted_edgelist(edgelistfp)

    # Node strength (degree disrtibution)

    # Edge weight distribution

    # Clustering coefficient distribution
    
    # connected components
    connected = [len(c) for c in sorted(nx.connected_components(g), key=len, reverse=True)]

    # Shortest path lengths
    # need efficient way to get the node pairs to show this distribution
    largest_cc = max(nx.connected_components(g), key=len)
    h = deepcopy(g.subgraph(largest_cc))
    #aspl = nx.average_shortest_path_length(h, weight='weight')
    #print('Average shortest path length of largest connected component ({} nodes, {:.2f}%) is {}.' .format(len(largest_cc), len(largest_cc)/len(g)*100, aspl))

    # Degree (strength) distribution
    st = [g.degree(n, weight='weight') for n in g.nodes()]
    v and print('Strengths computed')

    # Clustering coefficient distribution
    cc = [i for i in nx.clustering(g, weight='weight').values()]
    v and print('Clustering coefficients computed')
    
    fig = plt.figure(figsize=(10,5))
    fig.suptitle(title)
    axs = fig.subplots(1,3, sharey=False)
    params = dict(density=False, color='navy', alpha=1, log=True, align='left', rwidth=1)
    for ax in axs:
        ax.grid(axis='y', linestyle='--', linewidth=.42)
    axs[0].set(title='Connected components', xlabel='component size', ylabel='occurances')
    axs[0].hist(connected, bins=len(np.unique(st)), **params)
    axs[1].set(title='Node strength', xlabel='node strength', ylabel='occurances')
    axs[1].hist(st, bins=len(np.unique(st)), **params)
    axs[2].set(title='Clustering coefficient', xlabel='clustering coefficient', ylabel='occurances')
    axs[2].hist(cc, bins=len(np.unique(st)), **params)
    fig.tight_layout()
    try:
        fig.savefig(figfp)
        print('Figure {} saved to {}'. format(title, figfp))
    except Exception as e:
        print(e)

    return connected, st, cc



def vis_net(edgelistfp, _pos=None, recomputepos=False, niter=None, posfp=None, lcc_only=False, gexffp=None, visnetfp=None, title='', v=False):
    g = nx.read_weighted_edgelist(edgelistfp)
    
    if recomputepos:
        forceatlas2 = ForceAtlas2()
        pos = forceatlas2.forceatlas2_networkx_layout(g, pos=_pos, iterations=niter)

        try:
            with open(posfp, 'w') as f:
                json.dump(pos, f)
                print('Positions written to {}'. format(posfp))
        except Exception as e:
            print(e)
    else:
        pos = _pos

    if lcc_only:
        largest_cc = max(nx.connected_components(g), key=len)
        h = deepcopy(g.subgraph(largest_cc))
        g = h

    gexffp and nx.write_gexf(g, gexffp)

    if visnetfp:
        nodes = [n for n in g.nodes()]
        edges = [e for e in g.edges(data=True)]
        strengths = [g.degree(n, weight='weight') for n in nodes]
        weights = [e[2]['weight'] for e in edges]
        cmap = 'YlGnBu'
        alpha = .42
        params = dict(
                with_labels=False, 
                nodelist=nodes, 
                edgelist=edges,
                node_size=42,
                linewidths=.42,
                node_color=strengths, 
                edge_color=weights, 
                cmap=cmap, 
                vmin=min(strengths),
                vmax=max(strengths),
                alpha=alpha
                )

        fig = plt.figure(figsize=(9, 9))
        fig.suptitle(title)
        print('Drawing figure')
        nx.draw_networkx(g, pos, **params)
        fig.savefig(visnetfp)
        print('Figure {} written to {}'. format(title, visnetfp))

        if v:
            ndf = pd.DataFrame(strengths, nodes)
            edf = pd.DataFrame(weights, [(e[0], e[1]) for e in edges])
            print('-----\nNodes:\n{}\nEdges:\n{}\n'. format(ndf, edf))
            return g, pos, ndf, edf

    return g, pos
