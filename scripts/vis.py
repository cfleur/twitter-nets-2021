from fa2 import ForceAtlas2
from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib
import json
import warnings

def parse_net_components(rtedgelistfp, htedgelistfp, figfp=None, figtitle='Distribution of connected component sizes', v=True):
    rt_g = nx.read_weighted_edgelist(rtedgelistfp)
    rt_connected = [len(c) for c in sorted(nx.connected_components(rt_g), key=len, reverse=True)]
    rt_largest_cc = max(nx.connected_components(rt_g), key=len)
    rt_h = deepcopy(rt_g.subgraph(rt_largest_cc))

    ht_g = nx.read_weighted_edgelist(htedgelistfp)
    ht_connected = [len(c) for c in sorted(nx.connected_components(ht_g), key=len, reverse=True)]
    ht_largest_cc = max(nx.connected_components(ht_g), key=len)
    ht_h = deepcopy(ht_g.subgraph(ht_largest_cc))

    if figfp:
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



def vis_net_stats(rtg, htg, compute_paths=False, overviewfp=None, clusteringfp=None, v=True, vv=False):
    
    #sns.set_theme(style='whitegrid', font_scale=.5)
    matplotlib.rc_file_defaults()
    fig = plt.figure(figsize=(6,6))
    axs = fig.subplots(2, 2)
    params = dict(color='navy', alpha=.82)

    data = {}
    # note order of nodes and edges are not necessary for visualising histograms

    ### Stat overview ###
    if overviewfp:
        suptitle = 'Distribution of network statistics'
        fig.suptitle(suptitle)

        for g, name in zip((rtg,htg), ('retweets', 'hashtags')):
            # Node strength (degree disrtibution)
            strengths = [g.degree(n, weight='weight') for n in g.nodes()]
            data[name+'_strengths'] = strengths
            v and print('{} strengths recorded.'. format(name+'_strengths'))

            # Edge weight distribution
            weights = [e[2]['weight'] for e in g.edges(data=True)]
            data[name+'_weights'] = weights
            v and print('{} weights recorded.'. format(name+'_weights'))

            # Shortest path lengths
            if compute_paths:
                warnings.warn('Processing shortest path is slow, use smallest reasonable component.')
                if not nx.is_connected(g):
                    raise nx.NetworkXError("Graph is not connected.")
                aspl = nx.average_shortest_path_length(h, weight='weight')
                print('Average shortest path length of largest connected component is {}.' .format(aspl))

        # histogram
        subtitles = ['Retweet node strengths', 'Retweet edge weights', 'Hashtag node strengths', 'Hashtag edge weights']
        for ax, title, ylab, d in zip(axs.flat, subtitles, ('observations', '', 'observations', ''), (data['retweets_strengths'], data['retweets_weights'], data['hashtags_strengths'], data['hashtags_weights'])):
            vv and print(len(d), ax, title)
            ax.hist(d, bins=300, **params)
            ax.set(title=title, ylabel=ylab, yscale='log')
            ax.grid(axis='y', linestyle='--', linewidth=.42)
        fig.tight_layout()
        
        try:
            fig.savefig(overviewfp)
            print('Figure {} saved to {}'. format(suptitle, overviewfp))
        except Exception as e:
            print(e)
    
    ### Clustering ###
    if clusteringfp:
        suptitle = 'Distribution of clustering coefficients'
        fig.suptitle(suptitle)

        for g, name in zip((rtg,htg), ('retweets', 'hashtags')):
            clustering = [i for i in nx.clustering(g, weight='weight').values()]
            data[name+'_full_clustering'] = clustering
            v and print('{} clustering coefficients computed'. format(name+'_full_clustering'))

            # use lcc only
            largest_cc = max(nx.connected_components(g), key=len)
            h = deepcopy(g.subgraph(largest_cc))
            # Clustering coefficient distribution

            clustering = [i for i in nx.clustering(h, weight='weight').values()]
            data[name+'_lcc_clustering'] = clustering
            v and print('{} clustering coefficients computed'. format(name+'_lcc_clustering'))

        # histogram
        subtitles = ['Retweet full clustering', 'Hashtag full clustering', 'Retweet lcc clustering', 'Hashtag lcc clustering']
        for ax, title, ylab, d in zip(axs.flat, subtitles, ('observations', '', 'observations', ''), (data['retweets_full_clustering'], data['hashtags_full_clustering'], data['retweets_lcc_clustering'], data['hashtags_lcc_clustering'])):
            vv and print(len(d), ax, title)
            ax.hist(d, bins=300, **params)
            ax.set(title=title, ylabel=ylab, yscale='log')
            ax.grid(axis='y', linestyle='--', linewidth=.42)
        fig.tight_layout()

        try:
            fig.savefig(clusteringfp)
            print('Figure {} saved to {}'. format(suptitle, clusteringfp))
        except Exception as e:
            print(e)
    
        


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
