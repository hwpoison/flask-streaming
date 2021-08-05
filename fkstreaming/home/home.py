from flask import Blueprint, render_template, abort, send_from_directory, jsonify
from jinja2 import TemplateNotFound

from fkstreaming.api.utils import file_manage

home = Blueprint('home', __name__,
                        template_folder='templates')

@home.route('/', methods=['GET'])
def home_page():
    files = file_manage.get_files_by_type('video')
    if files:
        return render_template('home.html', files=files)
    else:
        return render_template('empty.html')