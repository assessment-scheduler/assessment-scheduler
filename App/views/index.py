from flask import Blueprint,render_template
from ..database import db
from ..controllers import initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')

# Gets Landing Page
@index_views.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
