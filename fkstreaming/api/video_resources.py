from flask import jsonify, request, send_from_directory, current_app, abort
from flask_restful import Resource

from fkstreaming.api.errors import MediaFileNotFound, MediaThumbnailNotFound, InternalServerError
from fkstreaming.api.utils import media_manage


class videoDownload(Resource):
	def get(self, id):
		current_app.logger.info(f'[+]Sending video {id}\n')
		path = media_manage.get_video_path(id)
		if path:
			return send_from_directory(
								directory=path.parent,
								path=     path.name)
		else:
			raise MediaFileNotFound

class videoFolder(Resource):
	def get(self, folder_id):
		folder = media_manage.get_folder(folder_id)
		if folder:
			return jsonify(folder)
		else:
			raise MediaFileNotFound

class videoThumb(Resource):
	def get(self, id):
		info = media_manage.get_video_info(id)
		if info:
			return send_from_directory(
								directory=media_manage.thumbnails_dir,
								path=info['thumb'])
		else:
			raise MediaThumbnailNotFound

class videoAll(Resource):
	def get(self):
		videos = media_manage.get_all_videos()
		if videos:
			return jsonify(videos)
		else:
			return MediaFileNotFound


class videoInfo(Resource):
	def get(self, id):
		info = media_manage.get_video_info(id)
		if info:
			return jsonify(info)
		else:
			raise MediaFileNotFound