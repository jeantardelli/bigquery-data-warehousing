import os

from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from google.cloud import bigquery

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

class StringForm(FlaskForm):
    string = StringField('String', validators=[DataRequired()])

# define your project.dataset.table.here
table_id = 'big-query-for-data-warehousing.main.stream'

# define number of repetitions you want
count = 1000

# you can modify the schema if you wish
schema = [
    bigquery.SchemaField("streamed_data", "STRING", mode="REQUIRED")
]

# define the root page
@app.route("/", methods=['GET', 'POST'])
def index():
    string = None
    form = StringForm()
    if form.validate_on_submit():
        string = form.string.data
        form.name.string = ''

    return render_template(
            'index.html',
            title='The UI for Data Streaming with Google App Engine',
            string=string,
            form=form,
            stream='stream'
        )

# define the behavior for loading the stream
@app.route("/stream", methods = ['POST'])
def stream():
    if "string" in request.form:
        string = request.form.get('string')
    else:
        return "No string passed", 500

    client = bigquery.Client()
    table = bigquery.Table(table_id, schema=schema)

    # the true ensures we will not get errors on subsequent runs of the script
    # when table already exists
    table = client.create_table(table, True)

    rows_to_insert = [{"streamed_data": string+str(i)} for i in range(count)]
    print(rows_to_insert)

    errors = client.insert_rows(table, rows_to_insert)
    if errors == []:
        return redirect('/')
    else:
        return errors, 500

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)
