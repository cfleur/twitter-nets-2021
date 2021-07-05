from time import time
from datetime import timedelta
import pandas as pd
import numpy as np

def format_tweets(tweets, retweets, ref_col='referenced_tweet_id', v=True, vv=False):
    '''Check data and format as dataframes'''

    tweetsdf = pd.DataFrame(tweets)
    retweetsdf = pd.DataFrame(retweets)

    # are all the original tweet references in the retweet dataset of length 1?
    lengths = np.unique([len(re) for re in retweetsdf[ref_col]])
    v and print('Unique lengths of referenced tweet column entries: {}'. format(lengths))
        
    multi_ref_count = 0

    for i, re_id in enumerate(retweetsdf[ref_col]):
        if len(re_id) > 1:
            entry = retweetsdf.iloc[i]
            multi_ref_count += 1
            vv and print('\n {} \n full ref data: {}\n'. format(entry, entry.full_ref_data))
    v and print('Number of multi-referenced entries: {}'. format(multi_ref_count))


    return tweetsdf, retweetsdf

def source_to_target(tweetsdf, retweetsdf, ref_col='referenced_tweet_id', id_col='tweet_id', author_col='author_id', v=False):
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


def write_edgelist(connectionlist, filepath):
    '''Writes edgelist file. '''
    pass

