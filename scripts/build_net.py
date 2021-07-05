from time import time
from collections import Counter
from datetime import timedelta
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools as it



def format_tweets(tweets, retweets, ref_col='referenced_tweet_id', v=True, vv=False):
    '''
    Check data and format as dataframes.
    Takes a list of tweet objects and a list of retweet objects and returns them as dataframes.
    Prints some summary statistics.
    '''

    tweetsdf = pd.DataFrame(tweets)
    retweetsdf = pd.DataFrame(retweets)
    v and print('Tweets formatted as dataframes. There are {} tweets and {} retweets.'. format(len(tweetsdf), len(retweetsdf)))

    # are all the original tweet references in the retweet dataset of length 1?
    lengths = np.unique([len(re) for re in retweetsdf[ref_col]])
    v and print('Unique lengths of referenced tweet column entries: {}'. format(lengths))
        
    # check multi-referencing tweets
    # multi-references means that a tweet references more than one original retweet, quote, reply
    # at the same time.
    multi_ref_count = 0

    for i, re_id in enumerate(retweetsdf[ref_col]):
        if len(re_id) > 1:
            entry = retweetsdf.iloc[i]
            multi_ref_count += 1
            vv and print('\n {} \n full ref data: {}\n'. format(entry, entry.full_ref_data))
    v and print('Number of multi-referencing entries: {}'. format(multi_ref_count))

    return tweetsdf, retweetsdf



def rt_source_to_target(tweetsdf, retweetsdf, ref_col='referenced_tweet_id', id_col='tweet_id', author_col='author_id', v=False):
    '''
    Takes a list of tweets and a list of retweets and identify source, targets,
    and counts number of timers a source connects to a targer (link weight)
    
    Args:
    -----
    tweetsdf: data frame
    retweetsdf: data frame
    
    Returns:
    -------
    "Connection list": list of all instances of connections between tweeters and retweeters.
    '''
    connectionlist = []
    data_issues = []
    non_match_tracker = 0
    t0 = time()

    for i in range(0, len(retweetsdf)):
        # 99.9999% done in 12:29:59.999762

        retweet = retweetsdf.iloc[i]
        original_ids = retweet[ref_col]
        v and print('Retweet no. {}:\n{}'. format(i, retweet))

        for oid in original_ids:
            original_tweet = tweetsdf.loc[tweetsdf[id_col] == oid]
            v and print('ORIGINAL TWEET:\n{}'. format(original_tweet))
            
            if len(original_tweet[author_col].values) == 1: 
                connection = {'source': original_tweet[author_col].values[0], 'target': retweet[author_col]}
                v and print('Recording connection: {}\n******\n'. format(connection)) 
                connectionlist.append(connection)
            
            elif len(original_tweet[author_col].values) > 1:
                v and print('More than one match!!!\n{}\n******\n'. format(original_tweet))
                data_issues.append((retweet, original_tweet))
            
            else:
                v and print('No matches.\n******\n')
                non_match_tracker += 1
            
            v and print('{:.4f}% done in {} .\n\n'. format((i/len(retweetsdf))*100, timedelta(seconds=time()-t0)))
    
    return connectionlist, data_issues, non_match_tracker



def process_hashtags(tweetsdf, tag_col='tags', tagusefp=None, tagspertweetfp=None, v=True, vv=False):
    ''' '''

    ### Number of tags per tweet ###
    # tweets with 0, 1, and more than 1 tags:
    tweets_with_multiple_tags = tweetsdf[tweetsdf[tag_col].str.len() > 1]
    tweets_with_one_tag = tweetsdf[tweetsdf[tag_col].str.len() == 1]
    tweets_without_tags = tweetsdf[tweetsdf[tag_col].str.len() == 0]
    v and print('------\nTweets with no tags {} ({:.4f}%).\nTweets with one tag {} ({:.4f}%).\nTweets with multiple tags {} ({:.4f}%).'. 
            format(len(tweets_without_tags), len(tweets_without_tags)/len(tweetsdf)*100,
                len(tweets_with_one_tag), len(tweets_with_one_tag)/len(tweetsdf)*100,
                len(tweets_with_multiple_tags), len(tweets_with_multiple_tags)/len(tweetsdf)*100))

    if tagspertweetfp:
        data = tweetsdf[tag_col].str.len().values
        bins = max(data)
        fig = plt.figure(figsize=(8,5))
        title = 'Distribution of number of tags per tweet'
        fig.suptitle(title)
        ax1 = fig.add_subplot(1,2,1)
        ax1.set(ylabel='number of occurances', xlabel='number of tags per tweet')
        ax1.grid(axis='y', linestyle='--', linewidth=.42)
        params1 = dict(color='navy', alpha=.82, log=False, density=False, align='left', rwidth=.82)
        ax1.hist(data, bins=bins, **params1)
        # add log version
        ax2 = fig.add_subplot(1,2,2)
        ax2.set(ylabel='', xlabel='number of tags per tweet')
        ax2.grid(axis='y', linestyle='--', linewidth=.42)
        params2 = dict(color='navy', alpha=.82, log=True, density=False, align='left', rwidth=.82)
        ax2.hist(data, bins=bins, **params2)
        fig.savefig(tagspertweetfp)
        v and print('------\nFigure "{}" has been written to {}'. format(title, tagspertweetfp))

    # investigate tag usage distribution
    tag_counts = tweets_with_multiple_tags[tag_col].explode().value_counts()
    once_used_sum = sum(tag_counts == 1)
    use_threshold = 10
    n_top = 40
    top_tags = tag_counts.head(n_top)
    v and print('------\nAmount of unique tags: {}'. format(len(tag_counts)))
    v and print('------\nAmount of tags used only once: {} ({:.2f}%)'. format(once_used_sum, once_used_sum/len(tag_counts)*100))
    v and print('------\nAmount of tags used {} times or less: {} ({:.2f}%)'. format(use_threshold, sum(tag_counts <= use_threshold), sum(tag_counts <= use_threshold)/len(tag_counts)*100))
    v and print('------\nTop {} tags:\n{}'. format(n_top, top_tags))

    if tagusefp:
        # uniform(-0.1, 0.1) adds jitter to x
        #i = [i+(i*r.uniform(-0.1, 0.1)) for i in range(0,len(tag_counts))]
        x = [i for i in range(0,len(tag_counts))]
        y = tag_counts
        if vv:
            print(len(tag_counts))
            print([(tc, i) for tc, i in zip(tag_counts,i)][0:50])
            print([(tc, i) for tc, i in zip(tag_counts,i)][-50:-1])
        fig = plt.figure()
        title = 'Distribution of hashtag usage'
        fig.suptitle(title)
        ax = fig.add_subplot(1,1,1)
        ax.grid(axis='y', linestyle='--', linewidth=.42)
        ax.set(yscale='log', ylabel='hashtag usage count', xlabel='hashtag index no.')
        style = dict(marker='|', alpha=.42, c='navy', s=12)
        ax.scatter(x, y, **style)
        fig.savefig(tagusefp)
        v and print('------\nFigure "{}" has been written to {}'. format(title, tagusefp))

    # hashtags used in a tweet without any other hashtags are not a part of the network
    hashtags = tweets_with_multiple_tags[tag_col]

    return hashtags, tag_counts



def ht_source_to_target(hashtags, htconnectionlistfp=None, v=False):
    '''
    A hashtag is linked to another if they appreared in the same tweet
    Parameters
    ----------
    hashtags: series/list-like (tags column of tweetsdf)
    '''

    # check length of tag arrays
    v and print('Min length tag array: {}. Max length tag array: {}.'. format(min(hashtags.str.len()), max(hashtags.str.len())))
   
    combinationsdf = hashtags.apply(lambda x: [c for c in it.combinations(x,2)])

    # check length of tag combination arrays (number of combinations = n(n-1)/2)
    v and print('Min length tag combination array: {}. Max length tag combination array: {}. Number of combinations = n(n-1)/2'. format(min(combinationsdf.str.len()), max(combinationsdf.str.len())))
    
    # number of pairs
    num_of_pairs = sum(combinationsdf.str.len())
    htconnectionlist = [{'source': i[0], 'target': i[1]} for i in it.chain(*combinationsdf.values)]
    v and print('{} connections recorded (should be {}).'. format(num_of_pairs, len(htconnectionlist)))

    if htconnectionlistfp:
        with open(htconnectionlistfp, 'w') as f:
            json.dump(htconnectionlist, f)
        v and print('-----\nHashtag connectionlist written to file {}.'. format(htconnectionlistfp))

    return htconnectionlist


def write_edgelist(connectionlist, filepath=None, v=True, vv=False):
    '''Writes edgelist file. '''
    
    c = Counter()    
    connectiondf = pd.DataFrame(connectionlist)
    setname = 'sourcetargetfs'
    links = []
    self_ref = 0

    # transform connection list into frozen set
    connectiondf[setname] = [frozenset([i, j]) for i, j in zip(connectiondf['source'], connectiondf['target'])]

    # count occurances of each set
    for fs in connectiondf[setname]:
        c[fs] += 1

    unique_connections = c.items()
    # the order of Counter.items() might be non-deterministic
    v and print('------\nThere are {} unique connections'. format(len(unique_connections)))

    # parse links
    for i in unique_connections:

        if len(i[0]) == 1:
            # author retweeted/replied/quoted themselves
            # hashtag used twice
            # network does not have self loops
            self_ref += 1
        
        elif len(i[0]) == 2:
            # correct length
            sourcetarget = list(i[0])
            source = sourcetarget[0]
            target = sourcetarget[1]
            count = i[1]
            link = source + ' ' + target + ' ' + str(count) + '\n'
            vv and print(link)
            links.append(link)

        else:
            print('source target length issue:\n{}'. format(i))

    v and print('------\n{} ({:.2f}%) are self-references (for tweet network author retweets/replies/qoutes themselves, for hashtags, tag is used twice in the same tweet).\nThese are not included in the edgelist (no self-loops).'. format(self_ref, self_ref/len(unique_connections)*100))
    v and print('------\n{} links recorded. Example link:\n{}'. format(len(links), links[-10]))

    if filepath:
        with open(filepath, 'w') as f:
            f.writelines(links)
        v and print('-----\nEdgelist written to file {}.'. format(filepath))
