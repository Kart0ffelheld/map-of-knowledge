import dash
import dash_core_components as dcc
import dash_html_components as html

from WikipediaArticle import suggest_article as getOptions

app = dash.Dash(__name__)
server = app.server

placeholder = "Enter your search here!"

app.layout = html.Div([
    html.H1("Map of Knowledge"),
    html.Div("Have fun with the progam!"),
    html.Br(),    
    
    html.Label(["Single dynamic Dropdown", dcc.Dropdown(id="search-dropdown", placeholder=placeholder)])
])

@app.callback(
    dash.dependencies.Output("search-dropdown", "options"),
    [dash.dependencies.Input("search-dropdown", "search_value")],
)
def update_options(search_value):
    dic_op = []    
    options = getOptions(search_value)
    
    for option in options:
        eintrag = {'label':option, 'value':option}
        dic_op.append(eintrag)
    return dic_op

@app.callback(
    dash.dependencies.Output("search-dropdown", "placeholder"),
    [dash.dependencies.Input("search-dropdown", "search_value")],
)
def update_placeholder(search_value):
    global placeholder
    if search_value: placeholder = search_value
    return placeholder


if __name__ == '__main__':
    app.run_server(debug=False)