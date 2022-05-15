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


class DirMediaManager(DirManager):
    """ Media file Manager  
        A set of methods to scan dirs and get specific files types
    """

    def __init__(self, root_path=Path.cwd()):
        DirManager.__init__(self, root_path)
        self.config_file = 'dirs.ini'
        self.folders = {}
        self.suppot_extensions = {}

    def get_dirs_from_config(self):
        """ parse config file 'dirs.ini' with user custom dirs """
        try:
            config.read(self.root_path.joinpath(self.config_file))
            return [Path(dir) for dir in config['DIRS']['video_dirs'].split('\n')]
        except configparser.ParsingError:
            raise Exception(
                "Error to parsing 'dirs.ini' file configuration, please check it!")

    def get_file_type(self, path: Path):
        """ This function clasify and filter entries by format extension """
        for type, formats in self.support_extensions.items():
            if path.suffix in formats and path.is_file():
                return type
        return False

    def sample_list(self, to_sample: list, k=6) -> list:
        if (amount := len(to_sample)) < k:
            k = amount
        sample = random.sample(to_sample, k)
        return sample

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
            dir_content = filter(self.get_file_type, self.iter(dir))

            # check if dir was modifiqued
            check = self.find_folder_by_path(dir)
            if check and check['id'] in self.folders:
                # update only if its newer
                if not self.was_modified(dir.stat(), self.folders[check['id']]['st']):
                    return True
            # get dir content
            dir_content = filter(self.get_file_type, self.iter(dir))
            files = {}

            for file in dir_content:
                id += 1
                files[id] = {
                    'path': file,
                    'type': self.get_file_type(file),
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


class FetchVideo(DirMediaManager):
    """ main class for fetch content form system directory """

    def __init__(self):
        DirMediaManager.__init__(self)
        self.thumbnails_dir = 'thumbnails/'
        self.support_extensions = {
            'video': ['.mp4', '.avi', '.flv', '.mkv'],
            'music': [],
            'subtitle': ['.srt', '.vvt']
        }

    def fetch_video_from_folder(self, folder_id, video_id):
        """ fetch and process video file info """
        if folder := self.folders.get(folder_id):
            if video := folder.get('files').get(video_id):
                return self.fetch_video_info(folder_id, video_id)

    def fetch_thumbnail(self, input_file: Path):
        output_dir = self.root_path.joinpath(self.thumbnails_dir)
        thumb = ffmpegUtils.generate_thumbail(
            input_file,
            output_dir.joinpath('thumbs/')
        )
        if not thumb:
            return "generic_thumb.png"
        return 'thumbs/' + thumb.name

    def search_video_by_name(self, string: str):
        results = self.find_file_by_name(string)
        all_coincidences = {}
        for id in results:
            info = self.fetch_video_info(id)
            if info:
                all_coincidences[id] = info

        return all_coincidences

    def find_video_by_id(self, video_id: int):
        for id, folder in self.folders.items():
            if video := folder.get('files').get(video_id):
                return video

    def find_video_subtitles(self, video_id: int):
        video = self.find_video_by_id(video_id)
        if video:
            # find a file with the same name but with .srt extension
            name_with_subtitle_extension = video['path'].stem + '.srt'
            for id, folder in self.folders.items():
                for id, file in folder['files'].items():
                    if file['path'].name == name_with_subtitle_extension:
                        return file['path']
        return False

    def fetch_video_info(self, video_id):
        file = self.find_video_by_id(video_id)
        if file['type'] == 'video':
            file_path = file['path']
            if not file.get('thumb'):
                file['thumb'] = self.fetch_thumbnail(file_path)
            return {
                'id': video_id,
                'title': file_path.stem,
                'thumb': file['thumb'] if 'thumb' in file else 'generic_thumb.png',
                'format': file_path.suffix,
            }
        return False

    def fetch_file_sample(self, file_list: list):
        sample = self.sample_list(file_list)
        return [self.fetch_video_info(file) for file in sample]

    def fetch_folder(self, id):
        self.update_index()
        if folder := self.folders.get(id):
            # main folder
            folder_content = map(self.fetch_video_info, folder['files'])
            folder_content = filter(lambda x: x, folder_content)
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
                        'file_samples': self.gen_folder_preview(sub_dir['id'])
                    }
            return dict_folder

        return False

    def fetch_video_path(self, video_id: int):
        if video := self.find_video_by_id(video_id):
            return video['path']
        return None

    def gen_folder_preview(self, folder_id: int):
        folder = self.folders.get(folder_id)
        only_video_files = filter(
            lambda x: folder['files'][x] if folder['files'][x]['type'] == 'video' else False, list(folder['files']))
        return self.fetch_file_sample(list(only_video_files))

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
                'file_samples': self.gen_folder_preview(folder['id'])
            }
        return folders


if __name__ == '__main__':
    media_manager = FetchVideo()
    media_manager.update_index()
    print(media_manager.folders)
else:
    media_manager = FetchVideo()
    media_manager.root_path = media_manager.root_path.joinpath('fkstreaming')
    media_manager.update_index()
