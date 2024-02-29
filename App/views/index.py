from flask import Blueprint, request, jsonify, render_template

index_views = Blueprint('index_views', __name__, template_folder='../templates')

# Main Index
@index_views.route('/', methods=['GET'])
def index():
    return render_template('index.html')