import os, re
#import functions from our type chart
import type_chart
import pandas as pd
import streamlit as st
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

#load types chart df
df = pd.read_excel('./Data/Pokemon Type Chart.xlsx')
df = df.set_index(df.columns[0])

############################
##### Query index
############################

def query_index(index_location, user_query):
    #open index
    ix = open_dir(index_location)
    
    with ix.searcher() as searcher:
        
        #load input query to parser
        query = QueryParser("content", ix.schema).parse(user_query)
        #search index for query
        results = searcher.search(query, terms=True, limit=10)
        
        results_list = []
        #iterate through response
        for res in results:
            results_list.append({"id": res['path'], "score": res.score,
                                 "text": res['content'], "source": res["file"]})
    return results_list

############################
##### App Format
############################

def transparent_background(col):
    return ['background-color: transparent' for _ in col]

def add_bg_from_url(url):
    st.markdown(
         f"""
         <style>
         .stApp {{
         color: black;
         background-image: url({url});
         background-attachment: fixed;
         opacity: 0.85;
         background-size: cover;
         }}
         p {{
         color: black;
         font-size:110%;
         margin: auto;
         }}
         h {{
         font-size:140%;
         margin: auto;
         }}
         .st-d0 {{
         background-color: transparent;
         }}
         .st-d1 {{
         background-color: transparent;
         }}
         .st-d2 {{
         background-color: transparent;
         }}
         .st-d3 {{
         background-color: transparent;
         }}
         .st-d4 {{
         background-color: transparent;
         }}
         .st-d5 {{
         background-color: transparent;
         }}
         .st-d6 {{
         background-color: transparent;
         }}
         .st-d7 {{
         background-color: transparent;
         }}
         .st-d8 {{
         background-color: transparent;
         }}
         .st-d9 {{
         background-color: transparent;
         }}
         table {{
         background-color: transparent;;
         font-color: black;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
#add background image in formatting
add_bg_from_url('https://i.redd.it/4ie5mv6bq6ma1.jpg') 

#header image and text
img_url = 'https://static.wikia.nocookie.net/pokemon-fano/images/6/6f/Poke_Ball.png'
header_html = f"""<p style='text-align: center; color: white;font-size:200%'><img src={img_url} width=50 height=50> All Region Pokedex <img src={img_url} width=50 height=50></p>"""
st.markdown(header_html, unsafe_allow_html=True)

#create a text input box for the user
prompt = st.text_input('Input search here.')

if prompt:
    #pass the prompt to the LLM
    response = query_index('Pokedex', prompt)
    
    if len(response) > 0:
        #create a new tab for each response
        tab_labels = [re.findall("^.*", find['text'])[0] for find in response]
        tabs = st.tabs(tab_labels)

        i = 0
        for tab in tabs:
            with tab:
                #pokemon name
                pokemon = tab_labels[i].lower().strip()
                
                #name changes to format image url
                changes = [('galar', 'galarian'), ('alola', 'alolan'), ('[ ]+', '-'), ('\.', ''), (r"’", '')]
                for change in changes:
                    pokemon = re.sub(change[0], change[1], pokemon)
                
                #dynamic url for pokemon image
                url = f"https://img.pokemondb.net/sprites/home/normal/2x/{pokemon}.jpg"
                #write pokemon image
                img_html = f"""<center><img style='border:5px solid #000000' src={url} width=150; height=150></center>"""
                
                #columns to order pokemon name and picture
                _, name, pic, _ = st.columns([0.25, 0.25, 0.25, 0.25])
                
                #pokemon name in left middle column
                with name:
                    clean_name = re.sub('[ ]+', ' ', tab_labels[i].strip())
                    st.write(f"<br><center><h style='font-size:150%'>{clean_name}<h/></center>", unsafe_allow_html=True)
                
                #pokemon image in right middle column
                with pic:
                    st.markdown(img_html, unsafe_allow_html=True)
                    
                #new line for formatting
                st.write("<br>", unsafe_allow_html=True)
                
                #different bins from pokedex pdfs
                non_hisui_bins = ['Base Stats', 'Basic Information', 'Evolution', 'Size Information',
                                  'Breeding Information', 'Capability List', 'Skill List', 'Level Up Move List',
                                  'TM/HM Move List', 'Egg Move List', 'Tutor Move List']
                
                #hisuian specific list
                hisui_bins = ['Base Stats', 'Basic Information', 'Evolution', 'Size Information', 'Breeding Information',
                             'Capability List', 'Skill List', 'Level Up Move List', 'Tutor Move List']
                
                #list of columns we want to keep
                keep_bins = ['Evolution', 'Level Up Move List', 'TM/HM Move List', 'Egg Move List', 'Tutor Move List']
                
                #pokemon stats and information
                pokemon_name_len = len(tab_labels[i])
                stats = response[i]['text'][pokemon_name_len:]
                
                #get types
                types = type_chart.extract_types(stats, df.columns)
                
                #get strengths and resistances
                if isinstance(types, list):
                    attack, defense = type_chart.strength_resistance(df, types[0].upper(), types[1].upper())
                else:
                    attack, defense = type_chart.strength_resistance(df, types.upper())
                
                #show dataframe in streamlit
                defense = pd.DataFrame(defense.values(), index=defense.keys(), columns=['MODIFIER']).T
                #style defense
                defense.style.background_gradient("color: transparent;")
                #write to streamlit
                st.dataframe(defense, hide_index=True, use_container_width=True, height=80)
                
                #start pokemon stats string
                stats_string = "<center>"
                
                #add type to string
                if isinstance(types, list):
                    stats_string += f"Type:<br>{types[0].title()} /  {types[1].title()}"
                else:
                    stats_string += f"Type:<br>{types.title()}"
                
                #list of columns to iterate through
                if 'Hisui' in response[i]['source']:
                    info_bins = hisui_bins
                else:
                    info_bins = non_hisui_bins
                    
                #concatenate all instances we need from the info bins
                for m in range(len(info_bins)):
                    try:
                        if m == len(info_bins) - 1:
                            #string start location
                            start = re.search(info_bins[m], stats).start()
                            start_string_end = re.search(info_bins[m], stats).end()

                            #concatenate to string
                            info = re.sub('[ ]*\\n[ ]*', '<br>', stats[start:])
                            #header name
                            header_name = info[:start_string_end]

                            #only write specific columns that are needed for game
                            if info_bins[m] in keep_bins:
                                info = re.sub('<br>{2,}', '<br><br>', info)
                                stats_string += f"<br>{info}"
                        else:
                            #string start location
                            start = re.search(info_bins[m], stats).start()
                            start_string_end = re.search(info_bins[m], stats).end()
                            #string end location
                            end = re.search(info_bins[m+1], stats).start()

                            #concatenate to string
                            info = re.sub('[ ]*\\n[ ]*', '<br>', stats[start:end]).strip()
                            #header name
                            header_name = info[:start_string_end]

                            #clean up evolution info
                            if info_bins[m] == 'Evolution':
                                info = re.sub('Minimum', '', info)
                                info = re.sub('[ ]+(?=[0-9] - )', '<br>', info)

                            #only write specific columns that are needed for game
                            if info_bins[m] in keep_bins:
                                stats_string += f"<br>{info}"
                    except AttributeError:
                        continue
                #write the formatted pokemon stats to dashboard       
                st.write(f"{stats_string}</center>", unsafe_allow_html=True)
                i += 1
    else:
        st.write("No results found.")
