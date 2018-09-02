# Experimental attempt to generate useful lists of potential
# names for projects.
import re,sys

import requests
from pprint import pprint

def flatten(xs):
    """Return the input list in flattened form."""
    if len(xs) == 0:
        return []
    else:
        head = xs[0]
        if type(head) == list:
            return flatten(head) + flatten(xs[1:])
        else:
            return [head] + flatten(xs[1:])

def combine(aggregation,element):
    if aggregation == "":
        return(element)
    return "{}-{}".format(aggregation,element)

def obtain(endpoint,seeds):
    # This function expects seeds to be a list.
    assert type(seeds) == list
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
rhymes, rhyme_data = obtain('rel_rhy',seeds)

# If any of the rhymes are among any of the synonyms,
# those results should immediately be promoted to the
# top of the heap. For example, seeding with 
#       gear dog
# yields a suggestion of
#       cog-dog.

# [X] Take "canine gear" and return "dog cog".
# [ ] Next take "gear canine" and turn it into "cog dog".
print("len(rhymes) = {}, len(rhymes[0]) = {}".format(len(rhymes),len(rhymes[0])))

ssr_limit = 44
sr_limit = 5
synonym_synonym_rhymes = []
for i,seed in enumerate(seeds):
    synonym_rhyme_sets, synonym_rhyme_data = obtain('rel_rhy',synonyms[i][0:sr_limit])
    # synonym_rhyme_sets has a list of rhymes for each of the sr_limit 
    # synonyms.
    for k in range(0,len(synonym_rhyme_sets)):
        synonym_rhymes = synonym_rhyme_sets[k]
        for syn_rhyme_k_m in synonym_rhymes:
            name = ""
            for j in range(i+1,len(seeds)):
                if syn_rhyme_k_m in synonyms[j][0:ssr_limit]:
                    name = combine(synonyms[i][k],syn_rhyme_k_m)
                    synonym_synonym_rhymes.append(name)

if len(synonym_synonym_rhymes) > 0:
    print(" === Synonym-Synonym Rhymes === ")
    pprint(synonym_synonym_rhymes)
#############

top_rhyming_names = []

for i in range(0,len(seeds)):
    all_other_synonyms = flatten(synonyms[0:i]+synonyms[i+1:])
    for rhyme in rhymes[i]:
        if rhyme in all_other_synonyms:
            name = combine(rhyme,seeds[i])
            top_rhyming_names.append(name)
            name = combine(seeds[i],rhyme)
            top_rhyming_names.append(name)            

if len(top_rhyming_names) > 0:
    print(" *** Top rhyming names ***")
    for trn in top_rhyming_names:
        print(trn)
    print(" *** END Top rhyming names ***")

#if len(seeds) > 1:
#    for i,seed in enumerate(seeds):
#        # For each of the first [limit] rhymes, generate a list of 
#        # words that tend to come before that rhyme.
#        rhyme_predecessors,predecessor_data = obtain('rel_bgb',rhymes[i][0:limit])
#        rhyme_predecessors = [remove_common_words(xs) for xs in rhyme_predecessors]
#        #pprint(rhyme_predecessors)
#
#        rhyme_limit = int(round(limit/4.0))
#        for k in range(0,len(rhyme_predecessors)):
#            for pred_k in rhyme_predecessors[k][0:rhyme_limit]:
#                name = ""
#                for j,seed in enumerate(seeds):
#                    if i != j:
#                        name = combine(name,seed)
#                    else:
#                        name = combine(combine(name,pred_k),seed)
#                print(name)


########## Homophone-based names ##########
# Example: story => tale (synonym) => tail (synonym-homophone, though also a synonym-rhyme, I guess) => tailspin ==> talespin

# > python namer.py story spin 
# should produce somewhere in its output talespin

#shex_limit = 44
sh_limit = 2
synonym_homophone_extensions = []
for i,seed in enumerate(seeds):
    #print(i,synonyms[i])
    synonyms_plus = ([seed] + synonyms[i]) # plus the original seed
    synonym_homophone_sets, synonym_homophone_data = obtain('rel_hom',synonyms_plus[0:sh_limit])
    # synonym_homophone_sets has a list of homophones for each of the sr_limit 
    # synonyms.
    for k in range(0,len(synonym_homophone_sets)):
        synonym_homophones = synonym_homophone_sets[k]
        #print("   synonym_homophones = {}".format(synonym_homophones))
        for syn_homophone_k_m in synonym_homophones:
            #print("       s_h_k_m = {}".format(syn_homophone_k_m))
            front_sets, front_data = obtain('sp',["{}*".format(syn_homophone_k_m)])
            #pprint(front_sets) 
            for front_compounds in front_sets: # This is a list of lists.
                for front_compound in front_compounds:
                # Split the compound word, taking away the original (synonyms_plus[k])
                    original_word = syn_homophone_k_m
                    extension = re.sub(original_word,'',front_compound)
                    for j in range(0,len(synonyms)):
                        if extension in synonyms[j]:
                            name = synonyms_plus[k] + extension
                            print("This one seems really good: {}".format(name))
                            synonym_homophone_extensions.append(name)

            back_sets, back_data = obtain('sp',["*{}".format(syn_homophone_k_m)])

            for back_compounds in back_sets: # This is a list of lists.
                for back_compound in back_compounds:
                # Split the compound word, taking away the original (synonyms_plus[k])
                    original_word = syn_homophone_k_m
                    extension = re.sub(original_word,'',back_compound)
                    for j in range(0,len(synonyms)):
                        if extension in synonyms[j]:
                            name = extension + synonyms_plus[k]
                            print("This one seems really good: {}".format(name))
                            synonym_homophone_extensions.append(name)

if len(synonym_homophone_extensions) > 0:
    print(" === Synonym-Homophone Extensions === ")
    pprint(synonym_homophone_extensions)
