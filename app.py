import os, errno
from flask import Flask, request, flash, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from convert import convert_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['CONVERTED_FOLDER'] = '/tmp/converted'
app.secret_key = os.environ.get('SECRET_KEY', 'default secret do not use')


for folder in [app.config['UPLOAD_FOLDER'], app.config['CONVERTED_FOLDER']]:
    try:
        os.makedirs(folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


@app.route('/convert', methods=["POST"])
def convert():
    if request.method == 'POST':
        if 'img' not in request.files:
            flash('No file specified')
            return redirect("/")
        file = request.files["img"]
        if file.filename == '':
            flash('No file specified')
            return redirect("/")

        name = secure_filename(file.filename)
        image = os.path.join(app.config['UPLOAD_FOLDER'], name)
        file.save(image)
        size = max(int(request.form['emojisize']), 4)
        convert_image(image, write_img=True, write_screen=False, write_file=False, outdir=app.config['CONVERTED_FOLDER'],max_width=1920, max_height=1080, display_size=size)
        return redirect(url_for('get_image', filename=os.path.splitext(name)[0] + ".png"))


@app.route('/emojitized/<filename>')
def get_image(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename)


@app.route('/')
def home():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data action="/convert">
      <label>Emoji Size
      <input type=number name=emojisize value=8 />
      </label>
      <br />
      <label>Image
      <input type=file name=img>
      </label>
      <br />
      <input type=submit value=Upload>
    </form>
    '''
