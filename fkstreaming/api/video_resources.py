from flask import jsonify, request, send_from_directory, current_app, abort
from flask_restful import Resource

from fkstreaming.api.errors import MediaFileNotFound, MediaThumbnailNotFound, InternalServerError
from fkstreaming.api.utils import file_manage


class videoStream(Resource):
	def get(self, video_id):
		current_app.logger.info(f'[+]Sending {video_id}\n')
		videos = file_manage.get_files_by_type('video')
		if file:=videos.get(video_id):
			return send_from_directory(
								directory=file['file_path'],
								path=     file['file_name'])
		else:
			raise MediaFileNotFound

class videoThumb(Resource):
	def get(self, img_name):
		if img_name:
			return send_from_directory(
								directory="videos/thumbs/",
								path=img_name)
		else:
			raise MediaThumbnailNotFound

class videoAll(Resource):
	def get(self):
		videos = file_manage.get_files_by_type('video')
		if videos:
			return jsonify(videos)
		else:
			return MediaFileNotFound


class videoInfo(Resource):
	def get(self, video_id):
		videos = file_manage.get_files_by_type('video')
		if file:=videos.get(video_id):
			return jsonify(file)
		else:
			raise MediaFileNotFound