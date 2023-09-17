import re
import streamlit as st
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

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

def add_bg_from_url(url):
    st.markdown(
         f"""
         <style>
         .stApp {{
             color: white;
             background-image: url({url});
             background-attachment: fixed;
             background-size: cover
         }}
         p {{
        color: white;
        font-weight: bold;
        }}
        .st-d6 {{
        background-color: transparent;
        }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url('https://i.redd.it/4ie5mv6bq6ma1.jpg') 

#header image and text
img_url = 'https://static.wikia.nocookie.net/pokemon-fano/images/6/6f/Poke_Ball.png'
header_html = f"""<p style='text-align: center; color: white;font-size:200%'><img src={img_url} width=50 height=50> All Region Pokedex <img src={img_url} width=50 height=50></p>"""
st.markdown(header_html, unsafe_allow_html=True)


#pre-saved database location
database_loc = st.text_input("Enter the path to the document database.")
    
#create a text input box for the user
prompt = st.text_input('Input search here.')

if prompt:
    #pass the prompt to the LLM
    response = query_index(database_loc, prompt)
    #create a new tab for each response
    tab_labels = [re.findall("^.*", find['text'])[0] for find in response]
    tabs = st.tabs(tab_labels)
    
    i = 0
    for tab in tabs:
        with tab:
            #write it out to the screen
            st.write(f"{response[i]['text']}")
            i += 1