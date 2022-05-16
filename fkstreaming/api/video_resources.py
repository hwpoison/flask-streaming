from flask import jsonify, request, send_from_directory, current_app, abort
from flask_restful import Resource
import os

from fkstreaming.api.errors import MediaFileNotFound, MediaThumbnailNotFound, \
    InternalServerError, AuthenticationError, SearchLengthError, VideoSubtitleNotFound
from fkstreaming.utils.media_manager import media_manager
from fkstreaming.utils.video import transcode_manager
from fkstreaming.utils.auth import Auth


class videoDownload(Resource):
    @Auth.token_required
    def get(self, id):
        current_app.logger.info(f'\n[+]Sending video {id}\n')
        path = media_manager.fetch_video_path(id)
        if path:
            return send_from_directory(
                directory=path.parent,
                path=path.name)
        else:
            raise MediaFileNotFound


class videoFolder(Resource):
    @Auth.token_required
    def get(self, folder_id):
        folder = media_manager.fetch_folder(folder_id)
        if folder:
            return jsonify(folder)
        else:
            raise MediaFileNotFound


class videoThumb(Resource):
    @Auth.token_required
    def get(self, id):
        info = media_manager.fetch_video_info(id)
        if info:
            return send_from_directory(
                directory=media_manager.thumbnails_dir,
                path=info['thumb'])
        else:
            raise MediaThumbnailNotFound


class videoSubtitles(Resource):
    @Auth.token_required
    def get(self, id):
        subtitle = media_manager.find_video_subtitles(id)
        if subtitle:
            return send_from_directory(
                directory=subtitle.parent,
                path=subtitle.name)
        else:
            raise VideoSubtitleNotFound


class videoAll(Resource):
    @Auth.token_required
    def get(self):
        videos = media_manager.fetch_all_videos()
        if videos:
            return jsonify(videos)
        else:
            return MediaFileNotFound


class videoSearch(Resource):
    def get(self, string):
        if len(string) < 3:
            raise SearchLengthError
        result = media_manager.search_video_by_name(string)

        return result


class videoInfo(Resource):
    @Auth.token_required
    def get(self, id):
        info = media_manager.fetch_video_info(id)
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
    @Auth.token_required
    def get(self, id, segment_name):
        path = transcode_manager.work_path
        if path:
            return send_from_directory(
                directory=path,
                path=segment_name,
                mimetype='video/mp2t')
        else:
            raise MediaFileNotFound

# initialize hls encoding thread
class videoStream(Resource):
    @Auth.token_required
    def get(self, id):
        current_token = Auth.get_current_token()
        path = media_manager.fetch_video_path(id)
        manifiest = transcode_manager.new(path, current_token)
        print("===>", current_token, " stream started")
        if path:
            return send_from_directory(
                directory=manifiest.parent,
                path=manifiest.name,
                mimetype='application/vnd.apple.mpegurl')
        else:
            raise MediaFileNotFound

# finish hls encoding thread
class finishStream(Resource):
    @Auth.token_required
    def get(self):
        current_token = Auth.get_current_token()
        finish = transcode_manager.finish(current_token)
        print(transcode_manager.poll)
        if finish:
            return jsonify({"message": "success finish"})
        else:
            return jsonify({"message": "error"})
