# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_table as dt
import json
from collections import Counter
from datetime import datetime
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.config['suppress_callback_exceptions']=True

tweets_data=pd.read_csv("Tweets_Sentiment.csv",encoding="utf-8")
### Convert Datetime field from string to Datetime
tweets_data['Tweet_DateTime']=pd.to_datetime(tweets_data['datetime'])

tweets_data['date']=tweets_data['Tweet_DateTime'].dt.date
#print(tweets_data.head())

def generateNGram(text,n=2):
    tokens=text.split(" ")
    ngrams = zip(*[tokens[i:] for i in range(n)])
    n_grams= ["_".join(ngram) for ngram in ngrams]
    n_grams=[ngram for ngram in n_grams if not ngram.startswith("_")]
    n_grams=[ngram for ngram in n_grams if not ngram.endswith("_")]
    return n_grams

def generateBigrams(tweets):
    #tweets_dat=tweets[tweets['sentiment']==sentiment]
    tweet_text=tweets['cleaned_tweet'].tolist()
    return [" ".join(generateNGram(tweet)) for tweet in tweet_text]

def getMostCommon(reviews_list,topn=20):
    reviews=" ".join(reviews_list)
    tokenised_reviews=reviews.split(" ")
    freq_counter=Counter(tokenised_reviews)
    return freq_counter.most_common(topn)


def plotMostCommonWords(reviews_list,topn=50,sentiment="positive"):
    if sentiment=="all":
        color="blue"
    if sentiment=="positive":
        color="green"
    if sentiment=="negative":
        color="red"
    if sentiment=="neutral":
        color="orange"
    top_words=getMostCommon(reviews_list,topn=topn)
    data=pd.DataFrame()
    data['words']=[val[0] for val in top_words]
    data['freq']=[val[1] for val in top_words]
    fig = px.bar(data, y='words', x='freq',orientation='h')
    fig.update_traces(textfont_size=20,marker=dict(color=color))
    fig.update_layout(yaxis=dict(autorange="reversed"),title="Top Bigrams - "+sentiment.title())
    return fig


def getSentimentPie(tweets,sentiment_col="sentiment"):
    sentiment_dat=pd.DataFrame(tweets[sentiment_col].value_counts().reset_index()).rename(columns={"sentiment":"count","index":"sentiment"})
    sentiment_dat['sentiment'] = pd.Categorical(sentiment_dat['sentiment'], ["positive", "neutral", "negative"])
    sentiment_dat=sentiment_dat.sort_values(by="sentiment")
    colors=['green','orange','red']
    fig = go.Figure(data=[go.Pie(labels=sentiment_dat['sentiment'],values=sentiment_dat['count'],opacity=0.8,hole=0.3)])
    fig.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=20,marker=dict(colors=colors))
    fig.update_layout(clickmode="event+select",title="Tweets Sentiment Distribution")
    return fig

def getTimeline(tweets,sentiment_col="sentiment"):
    day_wise_tweets=tweets.groupby('date').size().reset_index().rename(columns={0:"total_tweets"})
    positive_tweets=tweets[tweets['sentiment']=="positive"].groupby('date').size().reset_index().rename(columns={0:"num_positive_tweets"})

    day_wise_tweets=pd.merge(day_wise_tweets,positive_tweets,on="date",how='left')
    day_wise_tweets['percent_postive']=(day_wise_tweets['num_positive_tweets']/day_wise_tweets['total_tweets'])*100


    negative_tweets=tweets[tweets['sentiment']=="negative"].groupby('date').size().reset_index().rename(columns={0:"num_negative_tweets"})
    neutral_tweets=tweets[tweets['sentiment']=="neutral"].groupby('date').size().reset_index().rename(columns={0:"num_neutral_tweets"})

    day_wise_tweets=pd.merge(day_wise_tweets,negative_tweets,on="date",how='left')
    day_wise_tweets=pd.merge(day_wise_tweets,neutral_tweets,on="date",how='left')

    day_wise_tweets['percent_negative']=(day_wise_tweets['num_negative_tweets']/day_wise_tweets['total_tweets'])*100
    day_wise_tweets['percent_neutral']=(day_wise_tweets['num_neutral_tweets']/day_wise_tweets['total_tweets'])*100


    hovertemplate ='<b>Date</b>: %{x}'+'<br><b>Count</b>: %{y:.2f}'+ '<br><b>Percentage</b>: %{text}<br>'


    fig=go.Figure([
    go.Bar(name="negative",x=day_wise_tweets['date'],y=day_wise_tweets['num_negative_tweets'],marker_color="red",opacity=0.8,hovertemplate=hovertemplate,text=day_wise_tweets['percent_negative']),

    go.Bar(name="neutral",x=day_wise_tweets['date'],y=day_wise_tweets['num_neutral_tweets'],marker_color="orange",opacity=0.8,hovertemplate=hovertemplate,text=day_wise_tweets['percent_neutral']),

    go.Bar(name="positive",x=day_wise_tweets['date'],y=day_wise_tweets['num_positive_tweets'],marker_color='green',opacity=0.8,hovertemplate=hovertemplate,text=day_wise_tweets['percent_postive'])
    ])

    fig.update_layout(barmode='stack',title="Day-wise Tweets Distribution",paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')

    return fig

def generate_table(dataframe,columns_list,sentiment,max_rows=10):
    df=dataframe[columns_list]
    df=df.rename(columns={'url':'Twitter Links','text':'Text','nbr_retweet':'Retweets','nbr_favorite':'Favourites','nbr_reply':'Number Of Replies','datetime':'Datetime','polarity':'Polarity','subjectivity':'Subjectivity'})
    if sentiment == "negative":
        df=df.sort_values(by="Polarity")
    else:
        df=df.sort_values(by="Polarity",ascending=False)
    df['Twitter Links']="https://twitter.com"+df['Twitter Links']
    table=dt.DataTable(
        id='tweet_table',
        columns=[{"name": i, "id": i } for i in df.columns],
        data=df.to_dict('records'),
        # editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        # fixed_rows={'headers': True, 'data': 10},
        # column_selectable="single",
        style_header={
            'fontWeight': 'bold',
            'textAlign': 'left'
        },
        style_cell={
            # 'height':'auto',
            'fontFamily': 'Open Sans',
            'textAlign': 'left',
            'minWidth' : '180px', 'width' : '180px', 'maxWidth' : '180px',
            # 'height': '60px',
            # 'padding': '2px 22px',
            # 'display':'inline-block',
            'whiteSpace' : 'normal',
            'overflowWrap' : 'break-word',
            'wordWrap' : 'break-word',
            # 'overflow': 'hidden',
            # 'textOverflow': 'ellipsis',
        },
        # row_selectable='single',
        # hidden_columns=['Twitter Links'],
        # row_selectable=True,
        # row_selectable="multi",
        # row_deletable=True,
        # selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
    )
    return table

row = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1("Cerner Tweet Dashboard"),
                    width={"size": 6, "offset": 3},
                ),
                html.Br(),
                # html.Div(id="header-2",children=str(min(tweets_data['date']))+" to "+str(max(tweets_data['date']))),
                # html.H5(children=str(min(tweets_data['date']))+" to "+str(max(tweets_data['date']))),


            ],
            style={'textAlign':'center',"backgroundColor":"#3aa2d6"},

        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H3(str(min(tweets_data['date']))+" to "+str(max(tweets_data['date']))),
                    width={"size": 6, "offset": 3},
                ),
                html.Br(),
            ],
            style={'textAlign':'center',"backgroundColor":"#3aa2d6"},

        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Reset",id="reset-button",external_link=True,href="/",className="float-right btn btn-danger"),
                    md = 12
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="sentiment-graph",children=[dcc.Graph(id="sentiment-pie",className="four columns",clickData={'points':[{'label':"positive"}]},figure=getSentimentPie(tweets_data))]),
                    md=4
                )
                ,
                dbc.Col(
                    dcc.Graph(id="positive-timeline",className="eight columns",figure=getTimeline(tweets_data)),
                    md=8
                )

            ]
        ),
        html.Div(id="row-index"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="top-words"),
                    md=4
                )
                ,
                dbc.Col(
                    html.Div(id="tweet-data-table"),
                    className = "table table-bordered table-hover table-responsive cell cell-1-1 dash-fixed-content",
                    width={"size": 8, "offset": 0},
                )

            ]
        ),
    ],
    className="container-fluid"
)
app.layout = row



# @app.callback(
#     Output(component_id='my-div', component_property='children'),
#     [Input('tweet_table', 'selected_columns')]
# )
# def update_text(selected_columns):
#     print("selected_columns",selected_columns)
#     return "Hiiii"

@app.callback(Output("top-words","figure"), [Input("sentiment-pie","clickData")])
def update_top_bigrams(sentiment_click):
    if "curveNumber" in sentiment_click['points'][0]:
        sentiment=sentiment_click['points'][0]['label']
        filtered_df=tweets_data[tweets_data['sentiment']==sentiment]
    else:
        filtered_df=tweets_data
        sentiment="all"
    bigrams_list=generateBigrams(filtered_df)
    return plotMostCommonWords(bigrams_list,topn=30,sentiment=sentiment)

# @app.callback(Output('row-index', 'children'),
#               [Input('tweet_table', 'active_cell'),
#                Input('tweet_table', 'data')])
# def get_active_letter(active_cell, data):
#     if not active_cell:
#         return ""
#     if active_cell:
#         row=active_cell['row']
#         dat=data[row]
#         url = dat['Twitter Links']
#         # url = "https://twitter.com" + url
#         # dcc.Link('url', href=url)
#         url = html.A("Link to external site", href=url, target="_blank")
#         # redirect(url, code=302)
#         # return url
#         return url



### When pie chart is clicked update  the datatable
@app.callback(Output("tweet-data-table","children"),
[Input("sentiment-pie","clickData")])
def update_table(sentiment_click):
    if "curveNumber" in sentiment_click['points'][0]:
        # print("in sentiment")
        label=sentiment_click['points'][0]['label']
        filtered_df=tweets_data[tweets_data['sentiment']==label]
        sentiment=label
    else:
        filtered_df=tweets_data
        sentiment="All"
    return generate_table(filtered_df,columns_list=['url','text','nbr_retweet','nbr_favorite','nbr_reply','datetime','polarity','subjectivity'],sentiment=sentiment)





if __name__ == '__main__':
    app.run_server(debug=True,port=8060)
