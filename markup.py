import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

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

placeholder = "Enter your search here!"

controls = dbc.Card(
    [
		# search term
        dbc.FormGroup(
            [
                dbc.Label("Search Term"),
                dcc.Dropdown(id="search-dropdown", placeholder=placeholder)
            ]
        ),
		# depth
        dbc.FormGroup(
            [
                dbc.Label("Depth "),
                dbc.Input(id='depth', type='number', placeholder='Set a depth', value='2')

            ]
        ),

        # max count
        dbc.FormGroup(
            [
                dbc.Label("Number of Branches"),
                dbc.Input(id='max-count', type='number', placeholder='Set an initial value', value='3')

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
                dbc.Button("Start", id="start-button", outline=True, color="primary", size="lg", className="mr-2", n_clicks=0),
	    	dbc.Button("Increase Depth", id="add-depth", outline=True, color="primary", size="sm", className="mr-2", n_clicks=0)
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

info_button = html.Div(
    [
        dbc.Button(
            "Info",
            id="info-button",
			outline=True,
			size="lg",
            className="mb-3",
            color="info",
            n_clicks=0,
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody("Enter a search term and click \"Start\" to start you search. Hovering over a node displays the summary down below. Clicking on a node starts a new search with the chosen node as your search term.")),
            id="info-text",
            is_open=False,
        ),
    ]
)

hover_text = dbc.Card(
    dbc.FormGroup([
        html.P(id="hover_text")
    ])
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title='MoK'



app.layout = html.Div([
    dbc.Container([
       dbc.Row([
            dbc.Col(html.H1("Map of Knowledge")),
            dbc.Col(html.Div(info_button), align="end", width=4),
        ]),
        dbc.Row([
            dbc.Col(html.H5("Have fun with the progam!")),
	]),
        html.Hr(),
        dbc.Row([
                dbc.Col(controls, md=4),
                dbc.Col(graph, md=8, align="top"),
            ],
        ),

        dbc.Row([
            dbc.Col(hover_text, md=12, align="center")
            ],
        ),
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
    html.P(id="alli")
])
