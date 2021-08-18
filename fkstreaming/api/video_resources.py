from flask import jsonify, request, send_from_directory, current_app, abort
from flask_restful import Resource
import os 

from fkstreaming.api.errors import MediaFileNotFound, MediaThumbnailNotFound, InternalServerError, AuthenticationError
from fkstreaming.utils.media_manage import media_manager
from fkstreaming.utils.streaming import transcode_manager
from fkstreaming.utils.auth import token_required


def isAuth(be): #TODO
    if not be:
        raise AuthenticationError

class videoDownload(Resource):
    @token_required
    def get(token, self, id):
        isAuth(token)
        current_app.logger.info(f'\n[+]Sending video {id}\n')
        path = media_manager.get_video_path(id)
        if path:
            return send_from_directory(
                                directory=path.parent,
                                path=     path.name)
        else:
            raise MediaFileNotFound

class videoFolder(Resource):
    @token_required
    def get(token, self, folder_id):
        isAuth(token)
        folder = media_manager.get_folder(folder_id)
        if folder:
            return jsonify(folder)
        else:
            raise MediaFileNotFound

class videoThumb(Resource):
    @token_required
    def get(token, self, id):
        isAuth(token)
        info = media_manager.get_video_info(id)
        if info:
            return send_from_directory(
                                directory=media_manager.thumbnails_dir,
                                path=info['thumb'])
        else:
            raise MediaThumbnailNotFound

class videoAll(Resource):
    @token_required
    def get(token, self):
        isAuth(token)
        videos = media_manager.get_all_videos()
        if videos:
            return jsonify(videos)
        else:
            return MediaFileNotFound

class videoInfo(Resource):
    @token_required
    def get(token, self, id):
        isAuth(token)
        info = media_manager.get_video_info(id)
        if info:
            return jsonify(info)
        else:
            raise MediaFileNotFound

class killAll(Resource):
    def get(self):
        print("KILLING")
        if os.sys.platform == 'win32':
            os.system('taskkill /f /im ffmpeg.exe')
        else:
            os.system('pkill ffmpeg')

        print(transcode_manager.poll)
        transcode_manager.kill_all()

# sends hls stream segment
class videoStreamSegment(Resource):
    @token_required
    def get(token, self, id, segment_name):
        isAuth(token)
        path = transcode_manager.work_path
        if path:
            return send_from_directory(
                                directory=path,
                                path=     segment_name,
                                mimetype='video/mp2t')
        else:
            raise MediaFileNotFound

# initialize hls encoding thread         
class videoStream(Resource):
    @token_required
    def get(token, self, id):
        isAuth(token)
        path = media_manager.get_video_path(id)
        manifiest = transcode_manager.new(path, token)
        print("===>", token, " stream started")
        if path:
            return send_from_directory(
                                directory=manifiest.parent,
                                path=     manifiest.name,
                                mimetype='application/vnd.apple.mpegurl')
        else:
            raise MediaFileNotFound

# finish hls encoding thread
class finishStream(Resource):
    @token_required
    def get(token, self):
        isAuth(token)
        print("tryyng finish ", token)
        finish = transcode_manager.finish(token)
        print(transcode_manager.poll)
        if finish:
            return jsonify({"message":"success finish"})
        else:
            return jsonify({"message":"error"})
