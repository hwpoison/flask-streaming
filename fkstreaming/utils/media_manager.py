import os
import time
import random
import configparser

from pathlib import Path

if __name__ == '__main__':
    pass
else:
    from .video import ffmpegUtils

config = configparser.ConfigParser()

# This module is used to manage media files, scanning dirs and make an index for the server


class DirManager:
    def __init__(self, dir: Path):
        self.root_path = dir
        self.tracking_files = {}

    def walk(self, path: Path):
        """ Walk into path and get dirs and files """
        return path.glob('**/*')

    def walk_dirs(self, path: Path):
        """ Walk into path and get subdirs """
        return path.glob('**/')

    def iter(self, dir_path: Path):
        """ Iter dir content """
        return dir_path.iterdir()

    def was_modified(self, actual: os.stat_result, last: os.stat_result):
        """ compare mtime from path stat """
        # only detect file modifications in folder (TODO: detect file modifications)
        if actual.st_atime > last.st_atime:
            return True
        return False


class FileManager(DirManager):
    """ Media file Manager  
        A set of methods to scan dirs and get specific files types
    """

    def __init__(self, root_path=Path.cwd()):
        DirManager.__init__(self, root_path)
        self.config_file = 'dirs.ini'
        self.folders = {}

    def get_dirs_from_config(self):
        f""" parse config file '{ self.config_file }' with user custom dirs """
        try:
            config.read(self.root_path.joinpath(self.config_file))
            return [Path(dir) for dir in config['DIRS']['video_dirs'].split('\n')]
        except configparser.ParsingError:
            raise Exception(
                f"Error to parsing '{ self.config_file }' file configuration, please check it!")

    def sample_list(self, to_sample: list, k=6) -> list:
        if (amount := len(to_sample)) < k:
            k = amount
        sample = random.sample(to_sample, k)
        return sample

    def get_file_extension(self, path: Path):
        """ get file extension """
        return path.suffix

    def update_index(self):
        """ scan dirs and update index """
        # load dirs from config
        walk = []
        all_dirs = self.get_dirs_from_config()
        for dir in all_dirs:
            walk.extend(self.walk_dirs(dir))
        id = 0
        # add dir to the index
        for idx, dir in enumerate(walk):
            # scanning dirs
            dir_content = filter(self.get_file_extension, self.iter(dir))

            # check if dir was modifiqued
            check = self.find_folder_by_path(dir)
            if check and check['id'] in self.folders:
                # update only if its newer
                if not self.was_modified(dir.stat(), self.folders[check['id']]['st']):
                    return True
            # get dir content
            dir_content = filter(self.get_file_extension, self.iter(dir))
            files = {}

            for file_path in dir_content:
                id += 1
                files[id] = {
                    'path': file_path,
                    'extension': self.get_file_extension(file_path),
                }

            # add folder to the index
            if files:
                self.folders[idx] = {
                    'id': idx,
                    'path': dir,
                    'name': dir.name,
                    'files': files,
                    'is_root': dir in all_dirs,
                    'st':  dir.stat(),
                }

        return True

    def find_folder_by_path(self, path: Path):
        for id, dir_path in self.folders.items():
            if path == dir_path['path']:
                return dir_path
        return None

    def find_file_by_name(self, string: str):
        """ returns firts coincidence """
        for id, folder in self.folders.items():
            for id, file in folder['files'].items():
                if string.lower() in str(file['path'].name).lower():
                    yield id

    def get_root_folders(self):
        """ fetch only root folders (from dirs.ini)"""
        for path, info in self.folders.items():
            if info['is_root'] is True:
                yield path


class MediaManager(FileManager):
    """ main class for fetch content form system directory """

    def __init__(self):
        FileManager.__init__(self)
        self.thumbnails_dir = 'thumbnails/'
        self.supported_media_types = {
            'video': ['.mp4', '.avi', '.flv', '.mkv'],
            'music': ['.mp3', '.wav', '.flac', '.m4a'],
            'subtitle': ['.srt', '.vvt']
        }

        self.mimetypes = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'flac': 'audio/flac',
            'mp4': 'video/mp4',
            'avi': 'video/avi',
            'flv': 'video/flv',
            'mkv': 'video/mkv',
            'srt': 'text/srt',
            'jpg': 'image/jpeg',
            'm4a': 'audio/m4a',
            'png': 'image/png',
        }

    def find_media_by_id(self, media_id: int):
        for id, folder in self.folders.items():
            if mediaFile := folder.get('files').get(media_id):
                if self.is_supported_media_type(mediaFile):
                    return mediaFile

    def find_video_subtitles(self, video_id: int):
        video = self.find_media_by_id(video_id)
        if video:
            # find a file with the same name but with .srt extension
            name_with_subtitle_extension = video['path'].stem + '.srt'
            for id, folder in self.folders.items():
                for id, file in folder['files'].items():
                    if file['path'].name == name_with_subtitle_extension:
                        return file['path']
        return False

    def get_mimetype(self, file):
        """ get mimetype from file extension """
        return self.mimetypes.get(file['extension'][1:])

    def is_supported_media_type(self, file):
        """ check if file is supported """
        for media_type, extensions in self.supported_media_types.items():
            if file['extension'] in extensions:
                return media_type
        return False
    
    def get_media_type(self, file):
        return self.is_supported_media_type(file)


class FetchMedia(MediaManager):
    """ class for fetch media """

    def __init__(self):
        MediaManager.__init__(self)

    def fetch_media_path(self, media_id: int):
        if video := self.find_media_by_id(media_id):
            return video['path']
        return None

    def fetch_thumbnail(self, input_file: Path):
        output_dir = self.root_path.joinpath(self.thumbnails_dir)
        thumb = ffmpegUtils.generate_thumbail(
            input_file,
            output_dir.joinpath('thumbs/')
        )
        if not thumb:
            return "generic_thumb.png"
        return 'thumbs/' + thumb.name

    def fetch_main_preview(self):
        """ get preview of the root dirs """
        self.update_index()
        folders = {}
        for dir in self.get_root_folders():
            # fetch a sample preview of each folder
            folder = self.folders[dir]
            # sample only videos
            folders[folder['id']] = {
                'name': folder['name'],
                'file_samples':  self.fetch_folder_sample(folder)
            }
        return folders

    def folder_files(self, files):
        files = {id: file for id, file in files.items(
        ) if self.is_supported_media_type(file)}
        return [dict(self.file_info(file), **{'id': id}) for id, file in files.items()]

    def file_info(self, file):
        return {
            'title': file['path'].name,
            'mime': self.get_mimetype(file)
        }

    def media_info(self, id):
        """ get media info """
        media = self.find_media_by_id(id)
        if media:
            if not media.get('thumb'):
                media['thumb'] = self.fetch_thumbnail(media['path'])
            return {
                'id': id,
                'title': media['path'].name,
                'thumb': media['thumb'] if media.get('thumb') else 'generic_thumb.png',
                'mime': self.get_mimetype(media),
                'type': self.get_media_type(media),
            }

        return None

    def fetch_folder(self, id):
        """ fetch folder  and files (id, title) """
        self.update_index()
        if folder := self.folders.get(id):
            # main folder
            folder_content = self.folder_files(folder['files'])
            dict_folder = {
                'id': id,
                'name': folder['name'],
                'files': folder_content,
                'subdirs': {}
            }

            # subdirs folders and files preview sample
            for sdir in self.walk_dirs(folder['path']):
                if sdir != folder['path'] and (sub_dir := self.find_folder_by_path(sdir)):
                    dict_folder['subdirs'][sub_dir['id']] = {
                        'name': sub_dir['name'],
                        'file_samples': self.fetch_folder_sample(sub_dir)
                    }
            return dict_folder

        return False

    def fetch_folder_sample(self, folder):
        # shuffle [int, int, ...]
        sample = self.sample_list(list(folder['files']))
        return self.folder_files({id: folder['files'][id] for id in sample})

    def search_media_by_name(self, string: str):
        results = self.find_file_by_name(string)
        all_coincidences = {}
        for id in results:
            info = self.media_info(id)
            if info:
                all_coincidences[id] = info

        return all_coincidences


if __name__ == '__main__':
    pass
else:
    media_manager = FetchMedia()
    media_manager.root_path = media_manager.root_path.joinpath('fkstreaming')
    media_manager.update_index()
