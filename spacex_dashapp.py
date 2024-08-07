
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    html.Div([
        html.Div([
           
            dcc.Dropdown(id='site-dropdown',
                         options=[
                             {'label': 'All Sites', 'value': 'ALL'},
                             {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                             {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                             {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                             {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                         ],
                         value='ALL',
                         placeholder="Select a Launch Site here",
                         searchable=True
            ),
            html.Br(),
   
            html.Div(dcc.Graph(id='success-pie-chart')),
            html.Br(),
            html.P("Payload range (Kg):"),
            
            dcc.RangeSlider(
                id='payload-slider',
                min=0,
                max=10000,
                step=1000,
                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                value=[min_payload, max_payload] 
            ),
            html.Div(id='output-container-range-slider'),
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='success-payload-scatter-chart')
        ], className='six columns'),
    ], className='row')
])

@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_pie_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
        title = 'Total Success Launches for All Sites'
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title = f'Success vs Failure for {selected_site}'

    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
    
    success_count = filtered_df[filtered_df['class'] == 1]['class'].count()
    failure_count = filtered_df[filtered_df['class'] == 0]['class'].count()
   
    fig = go.Figure(data=[go.Pie(labels=['Success', 'Failure'],
                                 values=[success_count, failure_count],
                                 hole=0.3)])
    fig.update_layout(title=title)
    return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
        title = 'Correlation between Payload and Success for all Sites'
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Success for {selected_site}'
  
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
    
    fig = go.Figure()
 
    for booster_version in filtered_df['Booster Version Category'].unique():
        df_by_booster = filtered_df[filtered_df['Booster Version Category'] == booster_version]
        fig.add_trace(go.Scatter(x=df_by_booster['Payload Mass (kg)'],
                                 y=df_by_booster['class'],
                                 mode='markers',
                                 marker=dict(size=10),
                                 name=booster_version))
    fig.update_layout(title=title,
                      xaxis_title='Payload Mass (kg)',
                      yaxis_title='Class',
                      showlegend=True)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)