from flask import Blueprint, render_template, abort, send_from_directory, jsonify, \
request, make_response, url_for, redirect
from jinja2 import TemplateNotFound

from fkstreaming.utils.media_manage import media_manager
from fkstreaming.utils.auth import generate_token, register_token, sessions, token_required

home = Blueprint('home', __name__,
                        template_folder='templates')

def gen_token(resp):
    resp = make_response(resp)
    new_token = generate_token()
    register_token(new_token)
    resp.set_cookie('userToken', new_token)
    return resp

@home.route('/', methods=['GET'], endpoint="/")
def home_page():
    root_folders = media_manager.get_main_preview()
    if root_folders:
        resp = render_template('home.html', folders=root_folders)
    else:
        resp = render_template('empty.html')

    # generate token (Login)
    if token:=request.cookies.get('userToken'):
        if token not in sessions:
           resp = gen_token(resp)
    else:
        resp = gen_token(resp)
    return resp

@home.route('/<int:folder_id>', methods=['GET'])
@token_required
def view_folder(user, folder_id):
    if not user:
        return redirect(url_for('home./'))
    folder = media_manager.get_folder(folder_id)
    if folder:
        return render_template('view_folder.html', folder=folder)
    else:
        return render_template('empty.html')