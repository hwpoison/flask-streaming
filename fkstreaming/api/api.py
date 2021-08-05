from flask import request, Blueprint
from flask_restful import Api, Resource

from .errors import errors
from .video_resources import videoInfo, videoAll, videoStream, videoThumb

content_v1 = Blueprint('content_v1', __name__)

api = Api(content_v1, errors=errors)

api.add_resource(videoThumb,	'/video/thumb/<string:img_name>')
api.add_resource(videoStream, 	'/video/stream/<int:video_id>')
api.add_resource(videoInfo, 	'/video/<int:video_id>')
api.add_resource(videoAll,  	'/videos/', endpoint='videow')