import os
import re
import pandas as pd
import numpy as np

def extract_types(text, type_list):
    #use regex to find the string for the pokemons type
    types = re.findall('Type[ ]*:[ ]*([A-Za-z \/]+)', text)[0]
    #extract type differently if there is one or two types
    types = [typ.strip() for typ in types.split() if typ.upper() in type_list]
    types = types if len(types) > 1 else types[0]
    
    return types

def one_type(dataframe, type_1):
    #index location of type
    loc = dataframe.columns.get_loc(type_1)
    
    #instantiate dictionary for storage
    attack, defend = {}, {}

    #calculate all different type matchups for the attack
    attacks = pd.DataFrame(dataframe.iloc[loc]).T
    for atk_type in attacks.columns:
        if attacks[atk_type][attacks.index[0]] == 2:
            attack[atk_type] = 1.5
        elif attacks[atk_type][attacks.index[0]] == 0:
            attack[atk_type] = 0
        elif attacks[atk_type][attacks.index[0]] == 0.5:
            attack[atk_type] = 0.5

    #calculate all different type matchups for defense
    defense = pd.DataFrame(dataframe[dataframe.columns[loc]]).T
    for def_type in defense:
        if defense[def_type][defense.index[0]] == 2:
            defend[def_type] = 1.5
        elif defense[def_type][defense.index[0]] == 0:
            defend[def_type] = 0
        elif defense[def_type][defense.index[0]] == 0.5:
            defend[def_type] = 0.5
    return attack, defend

def combine_dicts(d1, d2):
    #iterate through
    d = {}
    for k, v in d1.items():
        if k in d2:

            #if no effect then keep no effect
            if (d1[k] == 0) or (d2[k]) == 0:
                val = 0
            #extra high
            elif (d1[k] == 1.5) and (d2[k] == 1.5):
                val = 2
            #extra low
            elif (d1[k] == 0.5) and (d2[k] == 0.5):
                val = 0.25
            #calculate average
            else:
                val = (d1[k] + d2[k]) / 2

            #set new value to key
            d[k] = val
            del d2[k]
        else:
            d[k] = d1[k]

    #update with remainder of dict_b
    d.update(d2)
    return d

def strength_resistance(dataframe, type_1, type_2 = None):
    #get attack and defense for both types
    atk1, def1 = one_type(dataframe, type_1)
    
    if type_2 is not None:
        #get second type stats
        atk2, def2 = one_type(dataframe, type_2)
    
        #compare both types to get
        attack = combine_dicts(atk1, atk2)
        defense = combine_dicts(def1, def2)
    else:
        attack = atk1
        defense = def1
    
    return attack, defense