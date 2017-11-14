import re,sys

import requests
from pprint import pprint

def combine(aggregation,element):
    if aggregation == "":
        return(element)
    return "{}-{}".format(aggregation,element)

def obtain(endpoint,seeds):
    xs = []
    x_data = []
    for seed in seeds:
        seed_parts = seed.split(' ')
        escape_seed = "+".join(seed_parts)
        r = requests.get(datamuse+"/words?{}={}".format(endpoint,escape_seed))
        xs.append([e['word'] for e in r.json()])
        x_data.append(r.json())
    return xs, x_data

def remove_common_words(xs):
    common_words = ['the', 'a', 'these', 'of', 'in', 'and', 'or', 'with']
    common_words += ['such', 'his', 'to', 'those', 'this', 'that', 'is']
    common_words += ['it', 'you', 'he', 'she', 'we', 'his', 'they', 'be']
    common_words += ['by', 'for', 'not', 'shall', 'may', 'can', 'will']
    common_words += ['would', 'could', 'might', 'must', 'should', 'much']
    common_words += ['nor', 'does', 'as', 'from', 'on', 'than', 'at']
    common_words += ['their', 'my', 'our', 'her', 'hers', 'him', 'its']
    common_words += ['was', 'were', 'been', 'had', 'each', 'one', 'your']
    common_words += ['have', 'who', 'are', 'into', 'whose', 'an']
    return [x for x in xs if x not in common_words]
# Take all command-line arguments after the script
# name as words/phrases that are inputs into making
# a project name.
# Currently, if n arguments are given, the suggested project
# names are all n words (or n phrases) long.
seeds = sys.argv[1:]

datamuse = "https://api.datamuse.com"
synonyms, synonym_data = obtain('ml',seeds)
rhymes, rhyme_data = obtain('rel_rhy',seeds)

# If any of the rhymes are among any of the synonyms,
# that results should immediately be promoted to the
# top of the heap.

limit = 10
print("======== SYNONYM-BASED NAMES ========")
for i,seed in enumerate(seeds):
    for word_i in synonyms[i][0:limit]:
        name = ""
        for j,seed in enumerate(seeds):
            if i != j:
                name = combine(name,seed)
            else:
                name = combine(name,word_i)
        print(name)

print("========= RHYME-BASED NAMES =========")
for i,seed in enumerate(seeds):
    # For each of the first [limit] rhymes, generate a list of 
    # words that tend to come before that rhyme.
    rhyme_predecessors,predecessor_data = obtain('rel_bgb',rhymes[i][0:limit])
    rhyme_predecessors = [remove_common_words(xs) for xs in rhyme_predecessors]
    #pprint(rhyme_predecessors)

    rhyme_limit = int(round(limit/4.0))
    for k in range(0,len(rhyme_predecessors)):
        for pred_k in rhyme_predecessors[k][0:rhyme_limit]:
            name = ""
            for j,seed in enumerate(seeds):
                if i != j:
                    name = combine(name,seed)
                else:
                    name = combine(combine(name,pred_k),seed)
            print(name)
