from flask import Blueprint, render_template, abort, send_from_directory, jsonify
from jinja2 import TemplateNotFound

from fkstreaming.api.utils import media_manage

home = Blueprint('home', __name__,
                        template_folder='templates')


@home.route('/', methods=['GET'])
def home_page():
    root_folders = media_manage.get_main_preview()
    if root_folders:
        return render_template('home.html', folders=root_folders)
    else:
        return render_template('empty.html')

@home.route('/<int:folder_id>', methods=['GET'])
def view_folder(folder_id):
    folder = media_manage.get_folder(folder_id)
    if folder:
        return render_template('view_folder.html', folder=folder)
    else:
        return render_template('empty.html')