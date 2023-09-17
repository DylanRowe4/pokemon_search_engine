import os, re
from langchain.document_loaders import PyPDFDirectoryLoader
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser

def add_pages_to_index(index_location):
    #add pdf to loader object
    loader = PyPDFDirectoryLoader('pdfs/pokedex_pdfs')
    print('Loading pdf pages...')
    #read pages of loader
    pages = loader.load()

    #remove table of contents pages
    pages = [page for page in pages if len(re.findall('\.', page.page_content)) <= 10]

    #remove the pokemons number before its name if the pdf starts with numbers instead of letters
    for page in pages:
        if re.search('^[0-9]{1,}', page.page_content):
            page.page_content = re.sub('^[0-9]{1,}', '', page.page_content)

    #create schema
    schema = Schema(path=ID(stored=True), content=TEXT(stored=True), file=TEXT(stored=True))

    #create new or load whoosh index
    if not os.path.exists(index_location):
        print("Creating new index...")
        os.mkdir(index_location)
        ix = create_in(index_location, schema)
    else:
        print("Appending to existing index...")
        ix = open_dir(index_location)

    #create a new writer object
    writer = ix.writer()

    #loop through pages and add documents to index
    for page in pages:
        if len(page.page_content) > 5:
            writer.add_document(path=f"{page.metadata['source']} - {page.metadata['page']}",
                                content=page.page_content,
                                file=page.metadata['source'].split('\\')[-1])
    writer.commit()

#use function to create index
add_pages_to_index('Pokedex')