import re,sys

import requests

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

# Take all command-line arguments after the script
# name as words/phrases that are inputs into making
# a project name.
# Currently, if n arguments are given, the suggested project
# names are all n words (or n phrases) long.
seeds = sys.argv[1:]

datamuse = "https://api.datamuse.com"
synonyms, synonym_data = obtain('ml',seeds)

limit = 10
for i,seed in enumerate(seeds):
    for synonym_i in synonyms[i][0:limit]:
        name = ""
        for j,seed in enumerate(seeds):
            if i != j:
                name = combine(name,seed)
            else:
                name = combine(name,synonym_i)
        print(name)
