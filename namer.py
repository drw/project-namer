import re,sys

import requests

def combine(aggregation,element):
    if aggregation == "":
        return(element)
    return "{}-{}".format(aggregation,element)

seeds = sys.argv[1:]

datamuse = "https://api.datamuse.com"
synonyms = []
synonym_parameters = []
for seed in seeds:
    seed_list = seed.split(' ')
    r = requests.get(datamuse+"/words?ml={}".format("+".join(seed_list)))
    synonyms.append([e['word'] for e in r.json()])
    synonym_parameters.append(r.json())

for i,seed in enumerate(seeds):
    for synonym_i in synonyms[i][0:5]:
        name = ""
        for j,seed in enumerate(seeds):
            if i != j:
                name = combine(name,seed)
            else:
                name = combine(name,synonym_i)
        print(name)
