from pathlib import Path
import dash
import os, sys
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go


# df = pd.read_csv(final_eq_path)


def make_traces(csv_path, x_axis, ignore_list=None, include_list=None, type='scatter'):
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
        raise ValueError(f"Cannot find file at {csv_path}.")

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
    if type == 'scatter':
        for i, col in enumerate(df.columns):
            if (df.columns[i] not in ignore_list) and (df.columns[i] in include_list):  # ensure agree with wanted columns
                graph = go.Graph(
                    x=df[x_axis],
                    y=df[col],
                    # text = df.columns[i],
                    mode='lines',
                    name=list(df)[i],
                    opacity=0.8,
                    # type=type
                )
                traces.append(graph)
    elif type == 'bar':
       for i, col in enumerate(df.columns):
            if (df.columns[i] not in ignore_list) and (df.columns[i] in include_list):
                graph = go.Bar(
                    x=df[x_axis],
                    y=df[col],
                    # text = df.columns[i],
                    # mode = 'markers',
                    name=list(df)[i],
                    opacity=0.8,
                    # type=type
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



def run_dash_server(folder_name, direct_run=False):
    """
    Runs the dashboard for a dataset

    Args:
        folder_name: Where the folder is located
        direct_run: True if running dashboard.py directly. This makes sure the relative paths are correct.

    Returns:

    """
    os.chdir(os.path.dirname(sys.argv[0]))  # Change current working directory to wherever dashboard.py is

    folder_path = f'../AM_programs/save_data/{folder_name}/'
    folder_path = (os.path.dirname(sys.argv[0]) + f'/AM_programs/save_data/{folder_name}/')
    folder_path = Path.cwd() / 'AM_programs' / 'save_data' / folder_name
    print("Folder Path:", folder_path)
    print(os.listdir(folder_path))

    chance_by_sum_path = folder_path / 'chance_by_sum.csv'
    final_eq_path = folder_path / 'final_eq.csv'
    totals_path = folder_path / 'totals.csv'
    average_eqs_path = folder_path / 'average_eqs.csv'
    single_spore_path = folder_path / 'single_strain_averages.csv'

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        dcc.Markdown(children=
                     f"### Metapopulation Simulation Results "),

        # dcc.Markdown(children="""#### Table of final equilibrium values"""),
        # generate_table(df),
        f"""This is the data from {folder_name}. The raw csvs are located in {folder_path}""",
        """--------------------------------------""",
        """Below is the population of each strain through time. Each strain has the sum of their vegetative and sporulated states. This graph also includes resources""",
        make_graph_from_csv(chance_by_sum_path, 'Strains through Time'),
        """Below is the same graph as above except with vegetative and sporulated cells plotted separately""",
        make_graph_from_csv(totals_path, 'Strains through Time (States Split)'),
        # Todo The below graph is dead for some reason.
        # """This graph is the final equilibrium values for the run.""",
        # make_graph_from_csv(final_eq_path, 'Final Eq Values', type='bar', ignore_list=['id'],
        #                     xaxis='Sporulation Probability'),
        """This graph is the total frequency of each equilibrium value after many runs""",
        make_graph_from_csv(average_eqs_path, 'Average Eqs', type='bar', ignore_list=['id'],
                            xaxis='Sporulation Probability'),
        """This is the eq value averaged across many runs for a single strain. X axis is the proportion to become spores.""",
        make_graph_from_csv(single_spore_path, 'Single Strain Curve', type='bar', ignore_list=['id'],
                            xaxis='Sporulation Probability'),
        """This ith the eq value averaged across many runs for two strains, where one strain is at sporulation strategy of .3""",
        make_graph_from_csv(folder_path / 'double_strain_averages.csv', 'Double Strain Curve', type='bar',
                            ignore_list=['id'], xaxis='Sporulation Probability'),

    ], style={'columnCount': 2})

    app.run_server()

if __name__ == "__main__":
    print("Starting Server")
    print(os.getcwd())
    run_dash_server('test997', direct_run=True)
