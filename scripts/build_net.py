import pandas as pd
import numpy as np

def format_tweets(tweets, retweets, v=True, vv=False):
    '''Check data and format as dataframes'''

    tweetsdf = pd.DataFrame(tweets)
    retweetsdf = pd.DataFrame(retweets)

    # are all the original tweet references in the retweet dataset of length 1?
    lengths = np.unique([len(re) for re in retweetsdf['referenced_tweet_id']])
    v and print('Unique lengths of referenced tweet column entries: {}'. format(lengths))
        
    multi_ref_count = 0

    for i, re_id in enumerate(retweetsdf.referenced_tweet_id):
        if len(re_id) > 1:
            entry = retweetsdf.iloc[i]
            multi_ref_count += 1
            vv and print('\n {} \n full ref data: {}\n'. format(entry, entry.full_ref_data))
    v and print('Number of multi-referenced entries: {}'. format(multi_ref_count))


    return tweetsdf, retweetsdf

def source_to_target(tweetsdf, retweetsdf):
    '''
    Takes a list of tweets and a list of retweets and identify source, targets,
    and counts number of timers a source connects to a targer (link weight)
    
    Args:
    -----
    tweetsdf: data frame
    retweetsdf: data frame
    
    Returns:
    -------
    Data structure with source, target and link weights.
    '''
    
    for i in range(0, len(tweetsdf)):
        original_id = tweetsdf.iloc[i]
        matching_retweets = retweets[[]]



