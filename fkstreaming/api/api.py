from flask import request, Blueprint
from flask_restful import Api, Resource

from .errors import errors
from .video_resources import videoInfo, videoAll, videoDownload, \
videoThumb, videoFolder, killAll, videoStream, videoStreamSegment, finishStream, videoSearch

content_v1 = Blueprint('content_v1', __name__)

api = Api(content_v1, errors=errors)

api.add_resource(videoAll,              '/videos/')                     # get all videos
api.add_resource(videoInfo,             '/videos/<int:id>')             # get video info
api.add_resource(videoThumb,            '/videos/<int:id>/thumb')       # fetch video thumbnail
api.add_resource(videoDownload,         '/videos/<int:id>/download')    # fetch video file
api.add_resource(videoFolder,           '/videos/folders/<int:folder_id>') # get video folder 
api.add_resource(videoSearch,           '/videos/find/<string>')   #search video
# stream endpoints
api.add_resource(videoStream,           '/videos/<int:id>/stream/start') # init stream/ get manifiest
api.add_resource(videoStreamSegment,    '/videos/<int:id>/stream/<segment_name>') # getsgment
api.add_resource(finishStream,          '/videos/stream/finish') # finish stream
api.add_resource(killAll,               '/killall') # finish all sever encoding procs.
