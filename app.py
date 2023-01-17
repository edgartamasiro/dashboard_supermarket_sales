
# IMPORTAÇÃO DE BIBLIOTECAS
import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from dash_bootstrap_templates import load_figure_template

# INSTANCIAÇÃO
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
load_figure_template('minty')
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server

# DATAFRAMES E PRÉ-PROCESSAMENTO DE DADOS
df_data = pd.read_csv('supermarket_sales.csv')
df_data['Date'] = pd.to_datetime(df_data['Date'])

# ESTRUTURAÇÃO DO LAYOUT DO DASHBOARD
app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="static/images/logo.png", top=True),
                dbc.CardBody([
                    html.H5('Cidades:'),
                    dcc.Checklist(df_data['City'].value_counts().index,
                    value=df_data['City'].value_counts().index, id='check-city',
                    inputStyle={'margin-right': '3px', 'margin-left': '5px'}),

                    html.H5('Variável de análise:', style={'margin-top': '50px'}),
                    dcc.RadioItems(['gross income', 'Rating'], value='gross income', id='main-variable',
                    inputStyle={'margin-right': '3px', 'margin-left': '5px'}),                
                ]),
                #html.H2('ASIMOV', style={'font-family': 'Voltaire', 'font-size': '40px'}),
                #html.Hr(),
            ], style={'height': '90vh', 'margin': '10px', 'padding': '10px'})
        ], sm=2),
        dbc.Col([
                # os graphs nascem zerados, serão preenchidos com figures através de callbacks
                dbc.Row([
                    dbc.Col([dcc.Graph(id='city-fig')], sm=4),
                    dbc.Col([dcc.Graph(id='gender-fig')], sm=4),
                    dbc.Col([dcc.Graph(id='pay-fig')], sm=4)
                ]),
                dbc.Row([dcc.Graph(id='income-per-date-fig')]),
                dbc.Row([dcc.Graph(id='income-per-product-fig')]),

        ], sm=10)
    ])

            ]
)

# CALLBACKS
@app.callback(
    [
        Output('city-fig', 'figure'),
        Output('pay-fig', 'figure'),
        Output('gender-fig', 'figure'),
        Output('income-per-date-fig', 'figure'),
        Output('income-per-product-fig', 'figure')
    ],
    [
        Input('check-city', 'value'),
        Input('main-variable', 'value')
    ]
)
def render_graphs(cities, main_variable):
    operation = np.sum if main_variable == 'gross income' else np.mean

    df_filtered = df_data[df_data['City'].isin(cities)]

    df_city = df_filtered.groupby('City')[main_variable].apply(operation).to_frame().reset_index()
    df_payment = df_filtered.groupby('Payment')[main_variable].apply(operation).to_frame().reset_index()
    df_product_income = df_filtered.groupby(['Product line', 'City'])[main_variable].apply(operation).to_frame().reset_index()
    df_gender = df_filtered.groupby(['Gender', 'City'])[main_variable].apply(operation).to_frame().reset_index()
    df_date_income = df_filtered.groupby('Date')[main_variable].apply(operation).to_frame().reset_index()

    fig_city = px.bar(df_city, x='City', y=main_variable)
    fig_payment = px.bar(df_payment, y='Payment', x=main_variable, orientation='h')
    fig_gender = px.bar(df_gender, x='Gender', y=main_variable, color='City', barmode='group')
    fig_product_income = px.bar(df_product_income, x=main_variable, y='Product line', color='City', orientation='h', barmode='group')
    fig_date_income = px.bar(df_date_income, y=main_variable, x='Date')

    for fig in [fig_city, fig_payment, fig_gender, fig_date_income]:
        fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200, template='minty')

    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=500)

    return fig_city, fig_payment, fig_gender, fig_date_income, fig_product_income

# MAIN
if __name__ == '__main__':
    app.run_server(debug=False)
    #app.run_server(debug=False, port=8080, host='0.0.0.0')






# FIM
