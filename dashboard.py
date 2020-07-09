import dash
import dash_core_components as dcc   
import dash_html_components as html 
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objects as go 
import pandas as pd
from dash.exceptions import PreventUpdate
import dash_table
import plotly.express as px

def get_stock_price_fig(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(mode="lines", x=df["Date"], y=df["Close"]))
    return fig

def get_dounts(df, label):

    non_main = 1 - df.values[0]
    labels = ["main", label]
    values = [non_main, df.values[0]]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.499)])
    return fig



app = dash.Dash(external_stylesheets=['<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">'])

app.layout = html.Div([
    
    html.Div([    
        html.P("Choose a Ticker to Start", className="start"),
        dcc.Dropdown("dropdown_tickers", options=[
        {"label":"Apple", "value":"AAPL"},
        {"label":"Tesla", "value":"TSLA"},
        {"label":"Facebook", "value":"FB"},
    ]),
        html.Div([
            html.Button("Stock Price", className="stock-btn", id="stock"),
            html.Button("Indicators", className="indicators-btn", id="indicators"),
        ], className="Buttons")

    ], className="Navigation"),

    html.Div([
        html.Div([
                html.P(id="ticker"),
                html.Img(id="logo"),
        ], className="header"), 
        html.Div(id="description", className="decription_ticker"),
        html.Div([
            html.Div([], id="graphs-content"),
        ], id="main-content")
    ],className="content"),

], className="container")


@app.callback(
            [Output("description", "children"), Output("logo", "src"), Output("ticker", "children"), Output("indicators", "n_clicks")],
            [Input("dropdown_tickers", "value")]
            )

def update_data(v):
    if v == None:
        raise PreventUpdate
    
    ticker = yf.Ticker(v)
    inf = ticker.info

    df = pd.DataFrame.from_dict(inf, orient="index").T
    df = df[["sector", "fullTimeEmployees", "sharesOutstanding", "priceToBook", "logo_url", "longBusinessSummary", "shortName"]]

    return  df["longBusinessSummary"].values[0], df["logo_url"].values[0], df["shortName"].values[0], 1


@app.callback(
            [Output("graphs-content", "children")],
            [Input("stock", "n_clicks")],
            [State("dropdown_tickers", "value")]
)

def stock_prices(v, v2):
    if v == None:
        raise PreventUpdate
    if v2 == None:
        raise PreventUpdate

    df = yf.download(v2)
    df.reset_index(inplace=True)

    fig = get_stock_price_fig(df)

    return [dcc.Graph(figure=fig)]


@app.callback(
            [Output("main-content", "children"), Output("stock", "n_clicks")],
            [Input("indicators", "n_clicks")],
            [State("dropdown_tickers", "value")]
)

def indicators(v, v2):
    if v == None:
        raise PreventUpdate
    if v2 == None:
        raise PreventUpdate
    ticker = yf.Ticker(v2)


    df_calendar = ticker.calendar.T
    df_info = pd.DataFrame.from_dict(ticker.info, orient="index").T
    df_info.to_csv("test.csv")
    df_info = df_info[["priceToBook", "profitMargins", "bookValue", "enterpriseToEbitda", "shortRatio", "beta", "payoutRatio", "trailingEps"]]
    
    

    df_calendar["Earnings Date"] = pd.to_datetime(df_calendar["Earnings Date"])
    df_calendar["Earnings Date"] = df_calendar["Earnings Date"].dt.date

    tbl = html.Div([
             html.Div([
        html.Div([
            html.H4("Price To Book"),
            html.P(df_info["priceToBook"])
        ]),
        html.Div([
            html.H4("Enterprise to Ebitda"),
            html.P(df_info["enterpriseToEbitda"])
        ]),
        html.Div([
            html.H4("Beta"),
            html.P(df_info["beta"])
        ]),
    ], className="kpi"), 
        html.Div([
            dcc.Graph(figure=get_dounts(df_info["profitMargins"], "Margin")),
            dcc.Graph(figure=get_dounts(df_info["payoutRatio"], "Payout"))
        ], className="dounuts")
        ])
       
    
    return [
        html.Div([tbl], id="graphs-content")], None



app.run_server(debug=True, port=8055)

