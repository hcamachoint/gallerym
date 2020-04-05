import glob
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask.cli import AppGroup
from flask_thumbnails import Thumbnail

app = Flask(__name__)
db = SQLAlchemy(app)
thumb = Thumbnail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['THUMBNAIL_MEDIA_ROOT'] = 'static/media'
app.config['THUMBNAIL_MEDIA_URL'] = '/media/'
app.config['THUMBNAIL_MEDIA_THUMBNAIL_ROOT'] = 'static/media/cache'
app.config['THUMBNAIL_MEDIA_THUMBNAIL_URL'] = '/media/cache/'

'''categories = db.table('image_category',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('images_id', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)'''

class Image(db.Model): #SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    #categories = db.relationship('Category', secondary='category', lazy='subquery', backref=db.backref('image', lazy='true'))
    created_at = db.Column(db.String(50), nullable=True)
    def __init__(self, name):
        self.name = name
        self.created_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

class Category(db.Model): #SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    slug = db.Column(db.String(), nullable=False)
    def __init__(self, name, slug):
        self.name = name
        self.slug = slug

class ImageCategory(db.Model): #SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

@app.route('/', methods=['GET'], defaults={"page": 1})
@app.route('/<int:page>', methods=['GET'])
def index(page):
    page = page
    per_page = 60
    data = Image.query.paginate(page, per_page)
    return render_template('index.html', images=data)


@app.route('/scan')
def scan():
    db.session.query(Image).delete()

    path = 'static/media/'
    files = [f for f in glob.glob(path + "**/*.jpg", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.JPG", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.jpeg", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.JPEG", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.png", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.PNG", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.gift", recursive=True)]
    files += [f for f in glob.glob(path + "**/*.GIFT", recursive=True)]
    data = []
    for f in files:
        newpic = Image(f.replace('static/media/', ''))
        db.session.add(newpic)

    db.session.commit()
    return redirect(url_for('index'))

db_cli = AppGroup('migrate') #CREO EL GRUPO DE MIGRATE

@db_cli.command('create')
def create_tables():
    db.create_all()
    print("Tables Created!")

@db_cli.command('refresh')
def refresh_tables():
    db.drop_all()
    print("Tables Deleted!")
    db.create_all()
    print("Tables Created!")

@db_cli.command('reset')
def reset_tables():
    db.drop_all()
    print("Tables Deleted!")

app.cli.add_command(db_cli)

if __name__ == '__main__':
    app.run(debug=True, host="12.7.0.0.1", port="5000")
