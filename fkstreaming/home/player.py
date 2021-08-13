from flask import Blueprint, render_template, abort, send_from_directory
from jinja2 import TemplateNotFound

from fkstreaming.api.utils import media_manage


player = Blueprint('player', __name__,
                        template_folder='templates')

@player.route('/play/<int:video_id>', methods=['GET'])
def getPlayer(video_id):
    info = media_manage.get_video_info(video_id)
    if info:
        return render_template('player/video_player.html', video_info=info)
    else:
        abort(404)