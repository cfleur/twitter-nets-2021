from pathlib import Path
import glob
import json
import pandas as pd

def parse_tweets(pattern, reldir, root, v=False, fwrite=False, fwritedir=None):
    '''
    pattern = '*_data_*.json'
    reldir = 'data/twitterdata/'
    root = './'
    fwritedir = 'output/parse/'
    '''

    imatches = glob.iglob(root + reldir + pattern)
    retweets = []
    original_tweets = []
    data_issue = []
    file_count = 0

    for match in imatches:
        v and print('... parsing file {}'. format(match))
        with open(match, 'r') as f:
            data = json.load(f)
            for d in  data:
                try:
                    tags = [hashtag['tag'] for hashtag in d['entities']['hashtags']]
                except:
                    tags = []

                try:
                    if len(d['referenced_tweets']) > 0:
                        retweets.append({
                                        'created_at': d['created_at'],
                                        'tweet_id': d['id'],
                                        'author_id': d['author_id'],
                                        'referenced_tweet_id': [re['id'] for re in d['referenced_tweets']],
                                        'full_ref_data': d['referenced_tweets'],
                                        'tags': tags 
                                        })
                    else:
                        original_tweets.append({
                                        'created_at': d['created_at'],
                                        'tweet_id': d['id'],
                                        'author_id': d['author_id'],
                                        'referenced_tweet_id': None,
                                        'tags': tags 
                                        })
                except:
                        data_issue.append({
                                        'created_at': d['created_at'],
                                        'tweet_id': d['id'],
                                        'author_id': d['author_id'],
                                        'referenced_tweet_id': 'undefined',
                                        'tags': tags 
                                        })
            file_count += 1

    v and print('***\n {} files parsed.\n***'. format(file_count))

    if fwrite:
        Path(root + fwritedir).mkdir(parents=True, exist_ok=True)

        datasets = [retweets, original_tweets, data_issue]
        names = ['retweets', 'original_tweets', 'data_issue']
        
        for n, d in zip(names, datasets):
            fname = n + '.json'
            
            with open(root + fwritedir + fname, 'w') as f:
                json.dump(d, f)

            v and print('wrote file {}'. format(root + fwritedir + fname))

        return


    return retweets, original_tweets, data_issue
