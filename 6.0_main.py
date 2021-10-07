import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate


from markup import controls, graph, hover_text, stylesheet, placeholder, app, server

from WikipediaArticle import WikipediaArticle
from WikipediaArticle import suggest_article as getOptions

# pip install dash_bootstrap_components

# TODO: Create mouse over label with first sentences / description
# TODO: Skip print outs on heroku for better performance

# erledigt: TODO: dropdown suggestions in different languages
# TODO: flag buttons for languages

# TODO: (performance) max_link_count should be in WikipediaArticle class, so that not all links will be generated, but only the first one will be shown
# TODO: checkbox: set max_link_count to -1 (/ALL)?

# TODO: if node already exists, create just new edge but not a new node


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

stage_T = []
stage_E = []

#%%

def getLinks (search_term, language, number_branches):
    '''
    To return ALL links, set count to -1.
    '''
    number_branches = int(number_branches)

    article = WikipediaArticle(search_term=search_term, language=language)
    article.get_links_in_summary()
    links = article.links_from_summary

    if len(links) > number_branches and not number_branches == -1: 
        return links[:number_branches]
        
    else:                                              
        return links

def createElements (title, mother):
    global all_searchTerms, elements, lang, next_id
    global stage_E, stage_T

    links = getLinks(title, lang, max_link_count)

    for i in range(len(links)):
        link = links[i]

        if link not in all_searchTerms:
            stage_T.append(link)

            # nodes
            label = link
            id = str(curr_depth)+"-"+str(next_id+i)
            eintrag = {'data': {'id': id, 'label': label}}
            stage_E.append(eintrag)

            # edges
            id0 = str(curr_depth-1)+"-"+str(mother)
            id1 = id
            eintrag = {'data': {'source': id0, 'target': id1}}
            stage_E.append(eintrag)

        else: raise Exception("Link schon vorhanden!")

    next_id += len(links)

def generateNextStage (term, lang):
    global elements, all_searchTerms
    global next_id, number_of_nodes
    global stage_E, stage_T

    if all_searchTerms == []:
        elements.append([{'data': {'id': "0-0", 'label': term}}])
        all_searchTerms.append([term])
        number_of_nodes = 1

    else:
        next_id = 0
        terms = all_searchTerms[-1]
        for i in range(len(terms)):
            term = terms[i]
            createElements(term, i)

        all_searchTerms.append(stage_T)
        elements.append(stage_E)
        stage_T = []
        stage_E = []

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
            # print(e)
        # print()

    is_running = False
    return list_of_elements, depth, str(curr_depth)+"/"+str(depth)


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
    if search_value: placeholder = search_value
    return placeholder


#%%

# Weiterleitung
@app.callback(Output('start-button', 'n_clicks'),
              Input('cytoscape', 'tapNodeData'), prevent_initial_call=True)

def displayTapNodeData(data):
    global topic
    topic = data['label']
    return -1


@app.callback(Output('hover_text', 'children'),
              Input('cytoscape', 'mouseoverNodeData'))

def displayHoverNodeData(data):
    print(stage_T)
    print("")
    print(stage_E)

    if data: return "Hallo, du schaust dir " + data['label'] + " an."


#%%
# Layout
@app.callback(Output('cytoscape', 'layout'),
              [Input('layout-dropdown', 'value')])

def update_cytoscape_layout(layout):
    return {'name': layout}


if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
