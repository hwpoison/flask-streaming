from flask import jsonify, request, send_from_directory, current_app
from flask_restful import Resource

from fkstreaming.api.utils import file_manage

class videoStream(Resource):
	def get(self, video_id):
		current_app.logger.info(f'[+]Sending {video_id}')
		videos = file_manage.get_videos()
		if file:=videos.get(video_id):
			print(file)
			return send_from_directory(
								directory=file['file_path'],
								path=     file['file_name'])
		else:
			return jsonify({'info':'parametros incorrectos'})

class videoPreview(Resource):
	def get(self, img_name):
		if img_name:
			return send_from_directory(
								directory="videos/thumbs/",
								path=img_name)
		else:
			return jsonify({'info':'image not found'})

class videoAll(Resource):
	def get(self):
		all_videos = file_manage.get_videos()
		if all_videos:
			return jsonify(all_videos)
		else:
			return jsonify({'info':'video not found!'})	

class videoInfo(Resource):
	def get(self, video_id):
		videos = file_manage.get_videos()
		if file:=videos.get(video_id):
			print(file)
			return jsonify(file)
		else:
			return jsonify({'info':'video not found!'})