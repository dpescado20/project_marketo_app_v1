import os

from flask import Flask, render_template, request, send_from_directory
from flask_uploads import UploadSet, configure_uploads, DATA

import pandas as pd

app = Flask(__name__)

docs = UploadSet('docs', DATA)

app.config['UPLOADED_DOCS_DEST'] = 'uploads'
configure_uploads(app, docs)

UPLOADED_FILES_PATH = 'uploads'
DOWNLOADED_FILES_PATH = 'downloads'


def upload():
    if request.method == 'POST' and 'doc' in request.files:
        docs.save(request.files['doc'])


def uploaded_files():
    files = []
    for filename in os.listdir(UPLOADED_FILES_PATH):
        path = os.path.join(UPLOADED_FILES_PATH, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def dysoi_process(df1, df2):
    df1.reset_index(level=0, inplace=True)
    df2.reset_index(level=0, inplace=True)

    df_shape1 = df1.shape
    max_row1 = df_shape1[0]

    df_shape2 = df2.shape
    max_row2 = df_shape2[0]

    df1['Describe Yourself_New'], df1['Solution of Interest_New'] = None, None

    dy1 = df1[df1.columns[1]].map(str) + df1[df1.columns[3]].map(str)
    # dy2 = df1[df1.columns[2]].map(str) + df1[df1.columns[4]].map(str)

    dy2a = df1[df1.columns[2]]
    dy2b = df1[df1.columns[4]]

    dy2a = dy2a.fillna('')
    dy2b = dy2b.fillna('')

    dy2a = dy2a.map(str)
    dy2b = dy2b.map(str)

    for i in range(max_row1):
        dy1_val = dy1.iloc[i]
        dy1_set = set(dy1_val.split(';'))

        for j in range(max_row2):
            if df2.iloc[j, 2] in dy1_set:
                df1.set_value(i, 'Describe Yourself_New', df2.iloc[j, 2])
                break

        dy2a_val = dy2a.iloc[i]
        dy2b_val = dy2b.iloc[i]
        dy2a_set = set(dy2a_val.split(';'))
        dy2b_set = set(dy2b_val.split(';'))

        dy2_set = dy2a_set.union(dy2b_set)
        dy2_list = list(filter(None, dy2_set))

        if len(dy2_list) > 1 and 'ALL' in dy2_list:
            dy2_list.remove('ALL')

        dy2_string = '; '.join(sorted(dy2_list))

        df1.set_value(i, 'Solution of Interest_New', dy2_string)

    df3 = df1[df1.columns[1:7]]

    output_file_name = 'process_output_dy_soi.xlsx'

    writer = pd.ExcelWriter('{}/{}'.format(DOWNLOADED_FILES_PATH, output_file_name))
    df3.to_excel(writer, 'Sheet1', index=False)
    writer.save()
    return output_file_name


@app.route('/', methods=['GET', 'POST'])
def run_process():
    upload()
    files = uploaded_files()

    if len(files) == 2:
        df1 = pd.read_csv('{}/{}'.format(UPLOADED_FILES_PATH, files[0]))
        df2 = pd.read_csv('{}/{}'.format(UPLOADED_FILES_PATH, files[1]))

        dysoi_process(df1=df2, df2=df1)
    return render_template('dysoi.html')


@app.route('/download/<path:path>')
def download(path):
    for filename in os.listdir(UPLOADED_FILES_PATH):
        os.remove(os.path.join(UPLOADED_FILES_PATH, filename))
    return send_from_directory(DOWNLOADED_FILES_PATH, path)


if __name__ == '__main__':
    app.run(debug=True)
