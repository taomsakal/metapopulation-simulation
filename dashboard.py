import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# df = pd.read_csv(final_eq_path)




def make_traces(csv_path, x_axis, ignore_list=None, include_list=None, type=None):
    """
    Make a trace for each column in the given csv file.

    Args:
        csv_path: Path to the csv file
        x_axis: The x axis of the graph. If it is none then use the first column
        ignore_list: A list of columns to not graph. If None then graphs all columns except the for the x-axis
        include_list: A list of columns that we only graph. If None then graph all columns
        type: The type of graph we want. Ex: put 'bar' for a bar graph. If None then is a line graph

    Returns:
        A list of traces
    """

    try:
        df = pd.read_csv(csv_path)  # Load the csv into a dataframe
    except ValueError:
        raise ValueError(f"Cannot find file at {csv_path}")

    # If x_axis is None then use the first column in the csv as x
    if x_axis is None:
        x_axis = df.columns[0]
    # Make ignore list empty if none
    if ignore_list is None:
        ignore_list = []
    # Make specific list all if None
    if include_list is None:
        include_list = list(df)

    ignore_list.append(x_axis)  # Never bother making a trace of the x-axis

    traces = []  # A list of traces (lines) that will be built from each column
    for i, col in enumerate(df.columns):
        if (df.columns[i] not in ignore_list) and (df.columns[i] in include_list): # ensure agree with wanted columns
            graph = go.Scatter(
                x = df[x_axis],
                y = df[col],
                # text = df.columns[i],
                # mode = 'markers',
                name = list(df)[i],
                opacity = 0.8,
                type = type
            )
            traces.append(graph)

    return traces



def make_graph_from_csv(csv_path, name, xaxis=None, type=None, ignore_list=None, include_list=None):
    """
    Makes a graph from a csv file. The first column is the x-axis and all the others get their own line.
    Args:
        csv_path: path to the csv file
        xaxis: the string for the x axis. If it is None then use the first column
        ignore_list: A list of columns to not graph. If None then graphs all columns except the for the x-axis
        include_list: A list of columns that we only graph. If None then graph all columns
        type: The type of graph we want. Ex: put 'bar' for a bar graph. If None then is a line graph

    Returns:
        a graph object?

    """

    traces = make_traces(csv_path, xaxis, type=type, ignore_list=ignore_list, include_list=include_list)
    return make_graph(traces, name)

def make_graph(traces, name):
    graph = dcc.Graph(
        id=f'{name} (Generated Graph)',
        figure={
            'data': traces,
            'layout': {'title': name}
        }
    )
    return graph




def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )



    # dcc.Graph(
    #     id='life-exp-vs-gdp',
    #     figure={
    #         'data': [
    #             go.Scatter(
    #                 x=df[df['continent'] == i]['gdp per capita'],
    #                 y=df[df['continent'] == i]['life expectancy'],
    #                 text=df[df['continent'] == i]['country'],
    #                 mode='markers',
    #                 opacity=0.7,
    #                 marker={
    #                     'size': 15,
    #                     'line': {'width': 0.5, 'color': 'white'}
    #                 },
    #                 name=i
    #             ) for i in df.continent.unique()
    #         ],
    #         'layout': go.Layout(
    #             xaxis={'type': 'log', 'title': 'GDP Per Capita'},
    #             yaxis={'title': 'Life Expectancy'},
    #             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
    #             legend={'x': 0, 'y': 1},
    #             hovermode='closest'
    #         )
    #     }
    # ),

    # html.Label('Dropdown'),
    # dcc.Dropdown(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value='MTL'
    # ),
    #
    # html.Label('Multi-Select Dropdown'),
    # dcc.Dropdown(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value=['MTL', 'SF'],
    #     multi=True
    # ),
    #
    # html.Label('Radio Items'),
    # dcc.RadioItems(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     value='MTL'
    # ),
    #
    # html.Label('Checkboxes'),
    # dcc.Checklist(
    #     options=[
    #         {'label': 'New York City', 'value': 'NYC'},
    #         {'label': u'Montréal', 'value': 'MTL'},
    #         {'label': 'San Francisco', 'value': 'SF'}
    #     ],
    #     values=['MTL', 'SF']
    # ),
    #
    # html.Label('Text Input'),
    # dcc.Input(value='MTL', type='text'),
    #
    # html.Label('Slider'),
    # dcc.Slider(
    #     min=0,
    #     max=9,
    #     marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
    #     value=5,
    # ),


def run_dash_server(folder_name):
    # global folder_path
    # folder_path = f'../AM_programs/save_data/test/'

    folder_path = f'../AM_programs/save_data/{folder_name}/'
    chance_by_sum_path = folder_path + 'chance_by_sum.csv'
    final_eq_path = folder_path + 'final_eq.csv'
    totals_path = folder_path + 'totals.csv'
    average_eqs_path = folder_path + 'average_eqs.csv'
    single_spore_path = folder_path + 'single_strain_averages.csv'

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        dcc.Markdown(children=
                     """### Crazy Cool Competition Colonization Computation """),

        # dcc.Markdown(children="""#### Table of final equilibrium values"""),
        # generate_table(df),

        make_graph_from_csv(chance_by_sum_path, 'Strains through Time'),
        make_graph_from_csv(totals_path, 'Strains through Time (States Split)'),
        make_graph_from_csv(final_eq_path, 'Final Eq Values', type='bar', ignore_list=['id'], xaxis='Sporulation Probability'),
        make_graph_from_csv(average_eqs_path, 'Average Eqs', type='bar', ignore_list=['id'], xaxis='Sporulation Probability'),
        make_graph_from_csv(single_spore_path, 'Single Strain Curve', type='bar', ignore_list=['id'], xaxis='Sporulation Probability'),
        make_graph_from_csv(folder_path + 'double_strain_averages.csv', 'Double Strain Curve', type='bar', ignore_list=['id'], xaxis='Sporulation Probability'),



    ], style={'columnCount': 1})

    app.run_server(debug=True)

# if __name__ == "__main__":
#     run_dash_server('test')