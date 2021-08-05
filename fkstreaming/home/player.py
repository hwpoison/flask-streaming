from flask import Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

from fkstreaming.api.utils import file_manage


player = Blueprint('player', __name__,
                        template_folder='templates')

@player.route('/play/<int:video_id>', methods=['GET'])
def getPlayer(video_id):
    videos = file_manage.get_files_by_type('video')
    if video:= videos.get(video_id):
        return render_template('player/video_player.html', video_info=video)
    else:
        abort(404)