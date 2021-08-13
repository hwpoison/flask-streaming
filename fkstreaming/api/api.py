from flask import request, Blueprint
from flask_restful import Api, Resource

from .errors import errors
from .video_resources import videoInfo, videoAll, videoDownload, videoThumb, videoFolder

content_v1 = Blueprint('content_v1', __name__)

api = Api(content_v1, errors=errors)

api.add_resource(videoAll,  	'/videos/') 					# get all videos
api.add_resource(videoInfo,		'/videos/<int:id>')		 		# get video info
api.add_resource(videoThumb,	'/videos/<int:id>/thumb') # get video thumbnail
api.add_resource(videoDownload,	'/videos/<int:id>/download') # get video file

#api.add_resource(videoFolders, 	'/videos/folders/') # get video folders
api.add_resource(videoFolder, 	'/videos/folders/<int:folder_id>') # get video folder 
