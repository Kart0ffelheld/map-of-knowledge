import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate


from markup import controls, graph, info_button, hover_text, stylesheet, placeholder, app, server

from WikipediaArticle import WikipediaArticle
from WikipediaArticle import suggest_article as getOptions

# pip install dash_bootstrap_components

"""
TODO: 
- Skip print outs on heroku for better performance
- flag buttons for languages
- checkbox: set max_link_count to -1 (/ALL)?
- communicate when running (spinner), show when errors occur
- Beautify mouse over description
    - Maybe use <iframe> ?
now:
- if node already exists, create just new edge but not a new node
- When Dropdown option is chosen entered text disappears
- When page is closen, server continues searches 
- More detailed Info text

DONE:
dropdown suggestions in different languages
"""

#%% set variables

curr_depth = -2
topic = ""
depth = 0
lang = ""
max_link_count = 3

is_running = False

all_searchTerms = []
elements = []

next_id = 0
number_of_nodes = 0

terms_curr_stage = []
elements_curr_stage = []


def getArticle (search_term, language, number_branches):
    '''
    To return ALL links, set number_branches to -1.
    '''
    number_branches = int(number_branches)

    article = WikipediaArticle(page_name = search_term, language = language)
    article.get_links_in_summary()

    if number_branches != -1: 
        article.filter(number_branches)
    
    elif number_branches == -1: # -1 Represents: get all links
        article.filtered_links_from_summary = article.links_from_summary

    return article

def createElements (title, mother):
    global all_searchTerms, elements, lang, next_id
    global elements_curr_stage, terms_curr_stage    # current stage/depth

    article = getArticle(title, lang, max_link_count)
    links = article.filtered_links_from_summary

    for i in range(len(links)):
        link = links[i]

        article_already_exists = False

        #Find out if article already exists
        for element in elements:
            for article in element:
                #elements is nested like this: [[[article_data: {"data": {"label": "blub"}}]], [{...},{...},{...}]]
                #Starting article is always elements[0]
            
                if ("label" in article["data"].keys()): 
                    #Has to be tested for to prevent errors
                    
                    if article["data"]["label"] == link:

                        #Make edge to exististing article
                        #Edge means "connection"
                        source_id = str(curr_depth - 1) + "-" + str(mother)
                        target_id = article["data"]["id"]

                        new_edge = {'data': {'source': source_id, 'target': target_id}}
                        elements_curr_stage.append(new_edge)
                        article_already_exists = True


        if article_already_exists == False:
            terms_curr_stage.append(link)
            # nodes
            label = link
            linked_article = getArticle(label, lang, max_link_count)
            linked_article = linked_article.toJSON()

            article_id = str(curr_depth) + "-" + str(next_id + i)
            
            new_article = {'data': {'id': article_id, 'label': label, 'wiki_object': linked_article}}
            elements_curr_stage.append(new_article)

            #Make edge to newly generated article
            #Edge means "connection"
            source_id = str(curr_depth - 1) + "-" + str(mother)
            target_id = article_id
            new_edge = {'data': {'source': source_id, 'target': target_id}}
            elements_curr_stage.append(new_edge)

    next_id += len(links)

def generateNextStage (term, lang):
    global elements, all_searchTerms
    global next_id, number_of_nodes
    global elements_curr_stage, terms_curr_stage

    if all_searchTerms == []:
        article = getArticle(term, lang, max_link_count)
        article = article.toJSON()

        elements.append([{'data': {'id': "0-0", 'label': term, 'wiki_object': article}}])
        all_searchTerms.append([term])
        number_of_nodes = 1

    else:
        next_id = 0
        terms = all_searchTerms[-1]
        for i in range(len(terms)):
            term = terms[i]
            createElements(term, i)

        all_searchTerms.append(terms_curr_stage)

        elements.append(elements_curr_stage)
        terms_curr_stage = []
        elements_curr_stage = []

        #print("ALL SEARCH TERMS")
        #print(all_searchTerms)

        #print("ELEMENTS")
        #print(elements)

# Start the search with a click on START, update search parameters
@app.callback(Output('elli', 'children'),
              [Input('start-button', 'n_clicks')],
              [State('search-dropdown', 'value'),
              State('depth', 'value'),
              State('max-count', 'value'),
              State('language-dropdown', 'value')], prevent_initial_call=True)

def initialize_search (n_klicks, top, dep, number_branches, lng):

    global topic, depth, max_link_count, lang, curr_depth
    global elements, all_searchTerms

    elements = []
    all_searchTerms = []

    curr_depth = -1

    if not n_klicks == -1:
        if top: topic = top
        else:   topic = placeholder

    depth = int(dep)
    max_link_count = number_branches
    lang  = lng

    return ""


# starts the update_elements def if depth is not reached yet
@app.callback(Output('ello', 'children'),
              Input('interval-component', 'n_intervals'))

def for_depth(v):
    global curr_depth, depth
    global is_running

    if not is_running and -2 < curr_depth < depth:
        is_running = True
        #return v
        #damit die Zahl nicht mehr erscheint und irritiert
    else: raise PreventUpdate

# updates the elements of cytoscape graph
@app.callback(Output('cytoscape', 'elements'),
              Output('depth', 'value'),
              Output('status', 'children'),
              Input('ello', 'children'),
              Input('add-depth', 'n_clicks'), prevent_initial_call=True)

def update_elements(v, n_klicks):
    global topic, lang, depth
    global curr_depth, is_running, depth

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'add-depth':
        depth += 1
        raise PreventUpdate

    curr_depth += 1
    generateNextStage(topic, lang)

    list_of_elements = []
    for el in elements:
        for e in el:
            list_of_elements.append(e)

    is_running = False
    #print("LIST OF ELEM")
    #print(list_of_elements)
    return list_of_elements, depth, str(curr_depth) + "/" + str(depth)


#%%
# Search suggestions
@app.callback(
    dash.dependencies.Output("search-dropdown", "options"),
    [dash.dependencies.Input("search-dropdown", "search_value")], prevent_initial_call=True)

def update_options(search_value):
    dic_op = []
    options = getOptions(search_value)

    for option in options:
        eintrag = {'label':option, 'value':option}
        dic_op.append(eintrag)
    return dic_op

@app.callback(
    dash.dependencies.Output("search-dropdown", "placeholder"),
    [dash.dependencies.Input("search-dropdown", "search_value")], prevent_initial_call=True)

def update_placeholder(search_value):
    global placeholder
    if search_value.strip() != "":    # Checks if search value is empty
        placeholder = search_value
    return placeholder


#%%

# Weiterleitung
@app.callback(Output('start-button', 'n_clicks'),
              Input('cytoscape', 'tapNodeData'), prevent_initial_call=True)

def displayTapNodeData(data):
    global topic
    topic = data['label']
    return -1


# info_button
@app.callback(Output("info-text", "is_open"),
              [Input("info-button", "n_clicks")],
              [State("info-text", "is_open")])
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

#summaries
@app.callback(Output('hover_text', 'children'),
              Input('cytoscape', 'mouseoverNodeData'))

def displayHoverNodeData(data):
    if data: 
        return data['wiki_object']['summary_text']


#%%
# Layout
@app.callback(Output('cytoscape', 'layout'),
              [Input('layout-dropdown', 'value')])

def update_cytoscape_layout(layout):
    return {'name': layout}


if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
