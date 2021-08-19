import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate

from WikipediaArticle import WikipediaArticle
from WikipediaArticle import suggest_article as getOptions

# pip install dash_bootstrap_components

# TODO: Join scripts
# TODO: Create mouse over label with first sentences / description
# TODO: Skip print outs on heroku for better performance

# TODO: dropdown suggestions in different languages
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

def getLinks (search_term, language, max_count):
    '''
    To return ALL links, set count to -1.
    '''
    max_count = int(max_count)
    
    article = WikipediaArticle(search_term=search_term, language=language)
    article.get_links_in_summary()
    links = article.links_from_summary
    
    if len(links) > max_count and not max_count == -1: return links[:max_count]
    else:                                              return links

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


#%%
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title='MoK'

stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)'
        }
    },
    {
        'selector': '[id = "0"]',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    },
    {
        'selector': 'edge',
        'style': {
        # The default curve style does not work with certain arrows
        'curve-style': 'bezier'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'target-arrow-color': 'lightblue',
            'target-arrow-shape': 'vee',
            'line-color': 'lightblue'
        }
    }
]

#%%

placeholder = "Enter your search here!"

controls = dbc.Card(
    [
		# search term
        dbc.FormGroup(
            [              
                dbc.Label("Search term"),
                #dcc.Dropdown(id="search-dropdown", placeholder=placeholder)
		dcc.Input(id='search-input')
            ]
        ),
		# depth
        dbc.FormGroup(
            [
                dbc.Label("Depth "),
                dbc.Button("+", id="add-depth", outline=True, color="primary", size="sm", className="mr-2", n_clicks=0),
                dbc.Input(id='depth', type='number', value='2', placeholder='Set a depth')
                
            ]
        ),
        
        # max count
        dbc.FormGroup(
            [
                dbc.Label("Max Count"),
                dbc.Input(id='max-count', type='number', value='3', placeholder='Set a max count')
                
            ]
        ),
        
		# language
        dbc.FormGroup(
            [
                dbc.Label("Language"),

				dcc.Dropdown(
		            id='language-dropdown',
		            options=[
		                {'label': 'english',
 		                 'value': 'en'},
		                {'label': 'french',
 		                 'value': 'fr'},
		                {'label': 'german',
 		                 'value': 'de'}
		            ], value='en', placeholder='Select a language'
		        ),
            ]
        ),
        
		# layout
        dbc.FormGroup(
            [
                dbc.Label("Layout"),
				dcc.Dropdown(
		            id='layout-dropdown',
		            options=[
		                #{'label': 'random',
		                # 'value': 'random'},
		                {'label': 'grid',
 		                 'value': 'grid'},
		                {'label': 'circle',
 		                 'value': 'circle'},
		                {'label': 'concentric',
 		                 'value': 'concentric'},
		                {'label': 'breadthfirst',
 		                 'value': 'breadthfirst'},
		                {'label': 'cose',
 		                 'value': 'cose'}
		            ], value='cose',
		        ),
            ]
        ),

		# start button
        dbc.FormGroup(
            [
                dbc.Button("Start", id="start-button", outline=True, color="primary", size="lg", className="mr-2", n_clicks=0)
            ]
        ),
    ],
    body=True,
)

graph = dbc.Card(
    dbc.FormGroup([
            cyto.Cytoscape(
                id='cytoscape',
                elements=[],
                style={
                    'height': '425px',
                    'width': '100%'},
                stylesheet=stylesheet
            ),
            html.P(id='status', children='status')
    ])
)

# card = dbc.Card(
#     dbc.FormGroup([
#             html.P(id='statue', children='statue')
#     ])
# )



app.layout = html.Div([
    dbc.Container([
        html.H1("Map of Knowledge"),
        html.H5("Have fun with the progam!"),
        html.Hr(),
        dbc.Row([
                dbc.Col(controls, md=4),
                dbc.Col(graph, md=8, align="top")
            ],
        )
    ]),# fluid=True),
    
    html.Div([
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ]),
   
    html.P(id='elli'),
    html.P(id="ello"),
    html.P(id="alli"),
    html.P(id="allo")
])

# Start the search with a click on START, update search parameters
@app.callback(Output('elli', 'children'),
              [Input('start-button', 'n_clicks')],
              [State('search-input', 'value'),
              State('depth', 'value'),
              State('max-count', 'value'),
              State('language-dropdown', 'value')])
def initialize_search (n_klicks, top, dep, max_count, lng):
    
    global topic, depth, max_link_count, lang, curr_depth
    global elements, all_searchTerms
    
    elements = []
    all_searchTerms = []
    
    curr_depth = -1
    
    if not n_klicks == -1:
        if top: topic = top
        else:   topic = placeholder
    
    depth = int(dep)
    max_link_count = max_count
    lang  = lng
    
    return ""


# starts the update_elements def if depth is not reached yet
@app.callback(Output('ello', 'children'),
              [Input('interval-component', 'n_intervals')])
def for_depth(v):    
    global curr_depth, depth
    global is_running
        
    if not is_running and -2 < curr_depth < depth:
        is_running = True
        return v
    else: raise PreventUpdate
    
# updates the elements of cytoscape graph
@app.callback([Output('cytoscape', 'elements'),
              Output('depth', 'value'),
              Output('status', 'children')],
              [Input('ello', 'children'),
              Input('add-depth', 'n_clicks')])
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
#@app.callback(
#    dash.dependencies.Output("search-dropdown", "options"),
#    [dash.dependencies.Input("search-dropdown", "value")])
#def update_options(search_value):
#    dic_op = []    
#    options = getOptions(search_value)
#    
#    for option in options:
#        eintrag = {'label':option, 'value':option}
#        dic_op.append(eintrag)
#    return dic_op
#
#@app.callback(
#    dash.dependencies.Output("search-dropdown", "placeholder"),
#    [dash.dependencies.Input("search-dropdown", "value")])
#def update_placeholder(search_value):
#    global placeholder
#    if search_value: placeholder = search_value
#    return placeholder


#%%

# Weiterleitung
@app.callback(Output('start-button', 'n_clicks'),
              [Input('cytoscape', 'tapNodeData')])
def displayTapNodeData(data):
    global topic
    topic = data['label']
    return -1


@app.callback(Output('allo', 'children'),
              [Input('cytoscape', 'mouseoverNodeData')])
def displayHoverNodeData(data):
    if data: return data['label']


#%%
# Layout
@app.callback(Output('cytoscape', 'layout'),
              [Input('layout-dropdown', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}



if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
