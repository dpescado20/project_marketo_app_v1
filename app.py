from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS

import pandas as pd

app = Flask(__name__)

docs = UploadSet('docs', DOCUMENTS)

app.config['UPLOADED_DOCS_DEST'] = 'uploads/docs'
configure_uploads(app, docs)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'doc' in request.files:
        filename = docs.save(request.files['doc'])
        df = pd.read_excel('uploads/docs/{}'.format(filename))
        print(df.head())
        return filename
    return render_template('dysoi.html')


if __name__ == '__main__':
    app.run(debug=True)
