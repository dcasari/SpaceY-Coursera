# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'}
                                     ]+[{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
                                        # Add other launch sites from spacex_df
                                        # Example: {'label': 'Site1', 'value': 'site1'},
                                    ],
                                    value='ALL',  # Default selected value
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total suc-cessful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0', 10000: '10000'},
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the corre-lation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total success counts for each launch site
        total_success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site')['class'].count()

        # Calculate total count for each launch site
        total_counts = spacex_df.groupby('Launch Site')['class'].count()

        # Calculate success percentages
        success_percentages = (total_success_counts / total_counts) * 100

        # Create a pie chart figure for total success for each launch site
        fig = px.pie(
            names=total_success_counts.index,
            values=success_percentages,
            title='Total Success for Each Launch Site',
            labels={'names': 'Launch Site'},
            hover_data={'values': total_success_counts, 'percentages': success_percentages},
            template='seaborn'  # You can choose a different template if needed
        )
    else:
        # Filter the DataFrame based on the selected launch site
         filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    # Calculate success counts for the filtered DataFrame
         success_counts = filtered_df[filtered_df['class'] == 1]['class'].count()
         failure_counts = filtered_df[filtered_df['class'] == 0]['class'].count()

        # Create a pie chart figure
         fig = px.pie(
            names=['Success', 'Failure'],
            values=[success_counts, failure_counts],
            title=f'Success vs Failure for {entered_site}' if entered_site != 'ALL' else 'Total Success vs Failure'
        )

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    # Filter the DataFrame based on the selected launch site and payload range
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    # Create a scatter plot figure
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs Launch Outcome for {entered_site}' if entered_site != 'ALL' else 'Payload vs Launch Outcome',
        labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        template='seaborn'  # You can choose a different template if needed
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8051)


