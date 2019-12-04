#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 09:40:00 2019

@author: anna_amato
"""

import json
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output, State
import flask
import dash_bootstrap_components as dbc

cyto.load_extra_layouts()
external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__,external_stylesheets=external_stylesheets,
meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

nodes = pd.read_csv("nodes_combined.csv")
edges = pd.read_csv("weightedlinks2.csv")


# Creating elements
data=[]
for index,row in nodes.iterrows():
    image=row["image"]
    name=row["author_id"]
    size=row["posts"]
    Role=row["Role"]
    degreeNorm=row["degreeNorm"]
    postsNorm=row["postsNorm"]
    betweenessNorm=row["betweenessNorm"]
    eigenvector=row["eigenvector"]
    
    data.append([name,image, size, Role, degreeNorm, postsNorm, betweenessNorm, eigenvector])

nodes = [
    { 'data': {'id': name, 'label': name.capitalize(), 'url': image, 'size':size, 'Role': Role,
               'degreeNorm':degreeNorm, 'postsNorm':postsNorm, 'betweenessNorm':betweenessNorm,
               'eigenvector':eigenvector
               }}
    for name, image, size, Role, degreeNorm, postsNorm, betweenessNorm, eigenvector in data
]

data=[]
for index,row in edges.iterrows():
    source=row["author_id"]
    target=row["parent"]
    weight=row["weight"]
    Reasoning=row["Reasoning"]
    Reflection=row["Reflection"]
    Elaboration=row["Elaboration"]
    Clarification=row["Clarification"]
    Alternative=row["Alternative"]
    Consensus=row["Consensus"]
    weightNorm=row["weightNorm"]
    
    data.append([source, target, weight, Reasoning, Reflection, Elaboration, Clarification,
                 Alternative, Consensus, weightNorm])
    
edges = [
    {'data': {'source': source, 'target': target, 'weight': weight, 'Reasoning': Reasoning, 'Reflection':Reflection,
             'Elaboration':Elaboration, 'Clarification':Clarification, 'Alternative':Alternative,
             'Consensus':Consensus, 'weightNorm': weightNorm}}
    for source, target, weight, Reasoning, Reflection, Elaboration, Clarification,
    Alternative, Consensus, weightNorm in data
]

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Creating styles
stylesheet = [
        
        
    {
       'selector': 'node',
        'style': {
            #'content': 'data(label)',
            'width': 'data(postsNorm)',
            'height': 'data(postsNorm)',
            'font-size':7,
            'font-family': 'sans-serif',
            'background-color':'#1e90ff'
        }
    },
        
 
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
            'haystack-radius': 0,
            #'width': 'data(weight)',
            'opacity': 'data(weightNorm)',
            'line-color': '#006ad1',
            'target-arrow-shape':'vee',
            'target-arrow-scale': 1,
            'target-arrow-color':'#1e90ff',
        }
    }, 

{
            'selector': '[Role *= "P"]',
            'style': {
                'background-color':'#70dc70',
                'color': '#26879b',
                'content': 'data(label)'
            }},

       
{
        'selector': '.Div',
        'style': {
            'width':'300px'
        }
    }
]
###############app layout elements 
navbar = dbc.NavbarSimple(className='navbar',
    children=[
        dbc.DropdownMenu(
            className='navbar',
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("HomePage", href='/homepage'),
                dbc.DropdownMenuItem("Bar Graphs", href='/bargraphs'),
                dbc.DropdownMenuItem("Social Network", href='/socialnetwork')
            ],
        ),
    ],
    brand="DataLiteracy CoDesign",
    brand_href="#",
    sticky="top",
)

body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Gallery Walk"),
                        html.H3(
                            """\
                            Data Visualizations"""
                        ),
                                html.Div(className='dropdown', children=[
                                        'Role:',
                                        dcc.Dropdown(id='input-bg-color', className='dropdown', clearable=True, options=[
                                                { 'label': name, 'value': name}
                                                for name in ['[Role *= "R"]' , '[Role *= "M"]', '[Role *= "A"]', '[Role *= "P"]']])
                                ]),
                                html.Div(className='dropdown', children=[
                                        'Centrality:',
                                        dcc.Dropdown(id='centrality', className='dropdown', clearable=True, options=[
                                                { 'label': name, 'value': name}
                                                for name in ['data(degreeNorm)' , 'data(betweenessNorm)', 'data(eigenvector)', 'data(postsNorm)']])
                                ]),
                                html.Div(className='dropdown', children=[ 
                                        'Number of Utterances:',
                                dcc.Dropdown(
                                        id='dropdown-update-weight',
                                        className= 'dropdown',
                                        multi=False,
                                        value='weight > 2',
                                        clearable=True,
                                        options=[
                                                {'label': name, 'value': name}
                                                for name in ['[weight < 3]', '[weight > 6]']
                                                ], 
                                        placeholder = "select number")
                                ]), 
                                html.Div(className='dropdown', children=[
                                        'Type of Dialogue:',
                                        dcc.Dropdown(id='input-line-color', className='dropdown', clearable=True, options=[
                                                {'label': name, 'value': name}
                                                for name in ['[Reasoning > 0]', '[Reasoning > 1]', 
                                                             '[Reflection > 2]', '[Clarification > 2]','[Elaboration > 2]',
                                                             '[Alternative > 2]','[Consensus > 2]']
                                                ])
                                ])
                                
                                
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Div([
                                cyto.Cytoscape(
                                        id='cytoscape-images',
                                        layout={'name': 'cola'},
                                        style={'width': '100%', 'height': '500px'},
                                        stylesheet=stylesheet,
                                        elements=nodes + edges
                                        ), 
                                        html.P(id='cytoscape-mouseoverNodeData-output'),
                                        html.P(id='cytoscape-mouseoverEdgeData-output')
                                        ])
                                ]),
                    ]
                ),
            ],
    className="mt-4",
        )
    


################ Declare app layout
app.layout = html.Div(children= [navbar, body])  

####tapnode callbacks 
@app.callback(Output('cytoscape-mouseoverNodeData-output', 'children'),
             [Input('cytoscape-images', 'mouseoverNodeData')])
def displayTapNodeData(data):
    if data:
        return data['Role'] + " " + data['label'] + " had " + str(data['size']) + " interactions." 


@app.callback(Output('cytoscape-mouseoverEdgeData-output', 'children'),
             [Input('cytoscape-images', 'mouseoverEdgeData')])
def displayTapEdgeData(data):
    if data:
        return data['source'] + " had " + str(data['weight']) + " contributions to " + data['target'] 
        
##########styles callback 
@app.callback(Output('cytoscape-images', 'stylesheet'), 
              [Input('input-line-color', 'value'),
           Input('input-bg-color', 'value'),
           Input('dropdown-update-weight', 'value'),
           Input('centrality', 'value')
           ])

def update_stylesheet(line_color, bg_color, update_weight, centrality):
    if line_color is None:
        line_color = ''

    if bg_color is None:
        bg_color = ''

    new_styles = [
        {
            'selector': bg_color,
            'style': {
                'background-fit': 'cover',
             'background-image': 'data(url)'
            }
        },
        {
            'selector': line_color,
            'style': {
                'line-color': '#ffa500',
                  'opacity': '.6'
            }
        },
            {
            'selector': update_weight,
            'style': {
                'line-color': '#92269b',
                'opacity': '.6'
            }
        }, 
            
             {
       'selector': 'node',
        'style': {
            #'content': 'data(label)',
            'width': centrality,
            'height': centrality,
            'font-size':7,
            'font-family': 'sans-serif'
        }
    }
            
    ]

    return stylesheet + new_styles

#element callback -- help
#@app.callback(Output('cytoscape-images', 'elements'),
#              [Input('dropdown-update-nodes', 'value')],
#              [State('cytoscape-images', 'elements')])
    
#def update_elements(elements):
#    
#    filtered_weighted = weightedlinks2[weightedlinks2['c'] == elements]
#    return len(filtered_weighted)
    


@app.server.route('/images/<image_path>.png')
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory("images", image_name)


if __name__ == '__main__':
    app.run_server(debug=True)