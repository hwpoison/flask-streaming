from flask import Blueprint, render_template, abort, send_from_directory, make_response, url_for, redirect
from jinja2 import TemplateNotFound
import time
import random

from fkstreaming.utils.media_manage import media_manager
from fkstreaming.utils.auth import token_required

player = Blueprint('player', __name__,
                        template_folder='templates')

@player.route('/play/<int:video_id>', methods=['GET'])
@token_required
def getPlayer(user, video_id):
    if not user:
        return redirect(url_for('home./'))
    info = media_manager.get_video_info(video_id)
    if info:
        return render_template('player/video_player.html', video_info=info)
    else:
        abort(404)

@player.route('/play/<int:video_id>/stream', methods=['GET'])
@token_required
def getStream(user, video_id):
    if not user:
        return redirect(url_for('home./'))
    info = media_manager.get_video_info(video_id)
    info['stream_id'] = user
    if info:
        return render_template('player/video_player_stream.html', video_info=info)
    else:
        abort(404)