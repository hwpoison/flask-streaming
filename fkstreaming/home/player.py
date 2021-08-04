from flask import Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

from fkstreaming.api.utils import file_manage


player = Blueprint('player', __name__,
                        template_folder='templates')

@player.route('/play/<int:video_id>', methods=['GET'])
def getPlayer(video_id):
    files = file_manage.get_videos()
    if video:= files.get(video_id):
        return render_template('player/video_player.html', video_info=video)
    else:
        abort(404)