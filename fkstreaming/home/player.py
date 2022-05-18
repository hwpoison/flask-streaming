from flask import Blueprint, render_template, abort, send_from_directory, make_response, url_for, redirect
from jinja2 import TemplateNotFound
import time
import random

from fkstreaming.utils.media_manager import media_manager
from fkstreaming.utils.auth import Auth

player = Blueprint('player', __name__,
                        template_folder='templates')

@player.route('/play/<int:video_id>', methods=['GET'])
@Auth.token_required
def getPlayer(video_id):
    info = media_manager.media_info(video_id)
    if info:
        return render_template('player/media_player.html', media_info=info)
    abort(404)

@player.route('/play/<int:video_id>/stream', methods=['GET'])
@Auth.token_required
def getStream(video_id):
    info = media_manager.media_info(video_id)
    info['stream_id'] = Auth.get_current_token()
    if info:
        return render_template('player/media_player_stream.html', media_info=info)
    abort(404)
