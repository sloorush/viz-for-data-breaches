#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dash
import dash_renderer
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # default styles for Dash apps

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Viz for data breaches'
app.scripts.config.serve_locally = True
server = app.server


### Load data ###
data = pd.read_csv('./data/breaches_clean.csv', thousands= ',')
data['SECTOR'] = data['SECTOR'].apply(lambda sector: sector.split(', '))
data.sort_values(by='records lost', inplace=True, ascending=False)

methods_list_names = ['All', 'Hacked', 'oops!', 'Poor security', 'Lost device', 'Inside job']
methods_list_values = ['all', 'hacked', 'oops!', 'poor security', 'lost device ', 'inside job']
methods_dict = { value: name for name, value in zip(methods_list_names, methods_list_values) }
method_options = [ { 'label': label, 'value': value} for label, value in zip(methods_list_names, methods_list_values) ]
method_color = {
    'all': '#0C0F25',
    'hacked' : '#903553',
    'oops!' : '#97BD5B',
    'poor security' : '#562972',
    'lost device ': '#EFAD24',
    'inside job': '#FFBAD2',
}

sector_list = ['web', 'retail', 'transport', 'government', 'telecoms',
        'app', 'healthcare', 'tech', 'financial', 'legal', 'gaming', 'media',
        'academic', 'energy', 'military']
sector_list.sort()
sector_list.insert(0, 'all')
sector_options = [ { 'label': sector, 'value': sector} for sector in sector_list ]


sensitivity_options = [
    {'value': 1, 'label': 'Just email address/Online information' },
    {'value': 2, 'label': 'SSN/Personal details' },
    {'value': 3, 'label': 'Credit card information' },
    {'value': 4, 'label': 'Health & other personal records' },
    {'value': 5, 'label': 'Full details' },
]

app.layout = html.Div(
    [
        dcc.Tabs([
        dcc.Tab(label='Presentation', children=[
            html.Div(
                [
                    html.Img(src=app.get_asset_url('dv.svg'),style = {'textAlign': 'center','max-width':'1400px'},)
                ],
                style = {'textAlign': 'center','background': '#0e1025', "color":"#fff"},
            )
        ]),
        dcc.Tab(label='Web-Security Visualization', children=[
        html.Div(
            [
                html.H1(
                    'Web-Security Visualization',
                    className='twelve columns',
                    id='title'
                ),
            ],
            style = {'textAlign': 'center'},
            className='row'
        ),
        html.Div(
            [
                html.P('Select methods used for the data breach:'),
                dcc.Dropdown(
                    id='methods-selector',
                    options=method_options,
                    multi=True,
                    value=['all'],
                    placeholder='Select method...',
                    clearable=False
                ),
            ],
            className='container'
        ),

        html.Div(
            [
                html.P('Filters:'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P('Filter by data sensitivity:'),
                                        dcc.Dropdown(
                                            id='data-sensitivity-select',
                                            options=sensitivity_options,
                                            multi=True,
                                            value=[1,2,3,4,5],
                                            placeholder='Select sensitivity options...',
                                        ),
                                    ],
                                    className='six columns'
                                ),
                                html.Div(
                                    [
                                        html.P('Filter by sector:'),
                                        dcc.Dropdown(
                                            id='sector-select',
                                            options=sector_options,
                                            multi=False,
                                            value='all',
                                            placeholder='Select sector...',
                                            clearable=False
                                        ),
                                    ],
                                    className='six columns'
                                ),
                            ],
                            className='row'
                        ),
                        html.Div(
                            [
                                html.P('Filter by data breach date:'),
                                dcc.RangeSlider(
                                    id='year-slider',
                                    min=2004,
                                    max=2021,
                                    value=[2004, 2021],
                                    marks={i: i for i in range(2004, 2021+1)},
                                ),
                            ],
                            className='row',
                            style={'margin-top': '20'}
                        ),
                    ],
                )
            ],
            className='container',
            style={'margin-top': '20'},
        ),

        html.Hr(),

        html.Div(id='graphs')])

      ])
    ]
)



def get_data_for_method (method: str, local_data: pd.DataFrame):
    if method == 'all':
        return local_data
    else:
        if method in methods_list_values:
            return local_data[local_data['METHOD'] == method]
        else:
            raise Exception('method not found')


def method_header(method_name: str, records_lost_no: int, companies_affected_no: int):
    return html.Div(
            [
                html.H5(
                    f'Data for method: "{method_name}"',
                    className='four columns',
                    style={'text-align': 'center'}
                ),
                html.H5(
                    [html.Strong("{:,}".format(int(records_lost_no))),' records lost.'],
                    className='four columns',
                    style={'text-align': 'center'}
                ),
                html.H5(
                    [html.Strong(companies_affected_no),' companies affected.'],
                    
                    className='four columns',
                    style={'text-align': 'right'}
                ),
            ],
            className='row container'
        )

@app.callback(
            Output('graphs', 'children'),
            [
                Input('methods-selector', 'value'),
                Input('year-slider', 'value'),
                Input('data-sensitivity-select', 'value'),
                Input('sector-select', 'value'),
            ]
    )
def make_main_figure(methods, years, selected_sensitivities, selected_sector):

    local_data = data.copy(deep=True)

    print(f'Years selected: {years}')
    list_years_set = list(range(years[0], years[1] + 1))
    local_data = local_data[local_data['YEAR'].isin(list_years_set)]

    print(f'Data sensitivity selected: {selected_sensitivities}')
    if selected_sensitivities != sensitivity_options:
        local_data = local_data [ local_data['DATA SENSITIVITY'].apply( lambda sensitivity: sensitivity in selected_sensitivities ) ]

    print(f'Sector selected: {selected_sector}')
    if selected_sector != 'all':
        local_data = local_data [ local_data['SECTOR'].apply( lambda sectors: selected_sector in sectors ) ]

    graphs = []
    print(f'Methods selected: {methods}')
    for method in methods:
        method_name = methods_dict[method]
        method_data = get_data_for_method(method, local_data)

        lost_data = method_data['records lost']
        entities = method_data['Entity']

        trace = dict(
            type='bar',
            x=len(lost_data),
            y=lost_data,
            text=entities,
            name='Records lost',
            marker=dict(
                color = method_color[method],
            )
        );

        layout = {
            'title': f'Records lost by "{method_name}" method(s)',

            'xaxis': {'title': 'Organization',
                        'titlefont': dict(
                            family='Courier New, monospace',
                            size=18,
                            color='#7f7f7f'
                    ),
            },
            'yaxis': {'title': 'Records lost',
                        'titlefont': dict(
                            family='Courier New, monospace',
                            size=18,
                            color='#7f7f7f'
                    )
            }
        }

        figure = dict(data=[trace], layout=layout)
        dash_graph = dcc.Graph(
                        id=f"graph-{method_name}",
                        figure=figure,
                        config={
                            'hovermode':  "y",
                            'showLink': False,
                            'modeBarButtonsToRemove': ['sendDataToCloud', 'lasso2d', 'select2d']
                        }
                    )

        graphs.append(html.Div(
            [
                method_header(method_name, lost_data.sum(), len(lost_data)),
                dash_graph,
                html.Hr()
            ],
            style={'margin-bottom': '10'}
        ))


    return graphs


if __name__ == '__main__':

    print('Using version ' + dash.__version__ + ' of Dash.')
    print('Using version ' + dash_renderer.__version__ + ' of Dash renderer.')
    print('Using version ' + dcc.__version__ + ' of Dash Core Components.')
    print('Using version ' + html.__version__ + ' of Dash Html Components.')

    app.server.run(debug=True, threaded=True)

