import base64
import os
from urllib.parse import quote as urlquote

from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

import pandas as pd

UPLOAD_DIRECTORY = "/Project_Marketo_App/app_uploaded_files"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


# app header
_navbar = dbc.NavbarSimple(
    children=[
    ],
    brand='Data Prox Master',
    brand_href='#',
    sticky='top'
)

# tab contents
tab1_content = (
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Upload(
                                    dbc.Button('Upload DY-SOI Data'),
                                    id='id-upload1',
                                    multiple=True)
                            ], width=3
                        ),
                    ]
                ),

                # line space
                dbc.Row(
                    [
                        html.Br()
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='id-lbl1')
                            ]
                        )
                    ]
                ),

                # line space
                dbc.Row(
                    [
                        html.Br()
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Upload(
                                    dbc.Button('Upload DY-SOI New Hierarchy'),
                                    id='id-upload2')
                            ], width=3
                        ),
                    ]
                ),

                # line space
                dbc.Row(
                    [
                        html.Br()
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='id-lbl2')
                            ]
                        )
                    ]
                ),

                # line space
                dbc.Row(
                    [
                        html.Br()
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button('Start Process', id='id-btn1', n_clicks=0)
                            ]
                        )
                    ]
                ),
                # line space
                dbc.Row(
                    [
                        html.Br()
                    ]
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='id-lbl3')
                            ]
                        )
                    ]
                )
            ]
        )
    )
)

# app body
_body = dbc.Container(
    [
        # line space
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Br()
                    ]
                )
            ]
        ),

        # tab creation
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(tab1_content, label='New DY-SOI'),
                                # dbc.Tab(tab2_content, label='Duplicate Tracker')
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
# app layout
app.layout = html.Div([_navbar, _body])


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def del_uploaded_file():
    for filename in os.listdir(UPLOAD_DIRECTORY):
        os.remove(os.path.join(UPLOAD_DIRECTORY, filename))


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output(component_id='id-lbl1', component_property='children'),
    [
        Input(component_id='id-upload1', component_property='filename'),
        Input(component_id='id-upload1', component_property='contents')
    ]
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    del_uploaded_file()
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    elif len(files) == 1:
        # return [html.Li(filename)for filename in files]
        return [html.Li(file_download_link(files[0]))]
    else:
        return [html.Li('Wrong Number of Files .. Please Check')]


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
