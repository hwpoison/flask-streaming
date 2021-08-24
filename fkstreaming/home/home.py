from flask import Blueprint, render_template, abort, send_from_directory, jsonify, \
request, make_response, url_for, redirect
from jinja2 import TemplateNotFound

from fkstreaming.utils.auth import Auth
from fkstreaming.utils.media_manager import media_manager

home = Blueprint('home', __name__,
                        template_folder='templates')

@home.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query')
        result = media_manager.search_video_by_name(query)
        return render_template('search_result.html', result=result)
    abort(404)
@home.route('/', methods=['GET'], endpoint="/")
def home_page():
    root_folders = media_manager.fetch_main_preview()
    if root_folders:
        resp = render_template('home.html', folders=root_folders)
    else:
        resp = render_template('empty.html')

    resp = Auth.login(resp)
    
    return resp

@home.route('/<int:folder_id>', methods=['GET'])
@Auth.token_required
def view_folder(folder_id):
    folder = media_manager.fetch_folder(folder_id)
    if folder:
        return render_template('view_folder.html', folder=folder)
    else:
        return render_template('empty.html')
