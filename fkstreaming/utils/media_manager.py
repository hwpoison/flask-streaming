import os
import time
import random
import configparser

from pathlib import Path

from .video import ffmpegUtils

config = configparser.ConfigParser()

class DirManager:
    def __init__(self, dir : Path):
        self.root_path = dir
        self.tracking_files = {}

    def walk(self, path : Path):
        """ Walk into path and get dirs and files """
        return path.glob('**/*')

    def walk_dirs(self, path : Path):
        """ Walk into path and get subdirs """
        return path.glob('**/')

    def iter(self, dir_path : Path):
        """ Iter dir content """
        return dir_path.iterdir()

    def compare_mtime(self, actual : os.stat_result , last : os.stat_result):
        """ compare mtime from path stat """
        if actual.st_mtime == last.st_mtime:
            return True 
        else:
            return False

class DirMediaManager(DirManager):
    """ Media file Manager  
        A set of methods to scan dirs and get specific files types
    """
    def __init__(self, root_path=Path.cwd()):
        DirManager.__init__(self, root_path)
        self.config_file = 'dirs.ini'
        self.folders = {}
        self.files = {}

    def get_dirs_from_config(self):
        """ parse config file 'dirs.ini' with user custom dirs """
        try:
            config.read(self.root_path.joinpath(self.config_file))
            return [Path(dir) for dir in config['DIRS']['video_dirs'].split('\n')]
        except configparser.ParsingError:
            raise Exception("Error to parsing 'dirs.ini' file configuration, please check it!")
    
    def get_file_type(self, path : Path):
        """ This function clasify and filter entries by format extension """
        for type, formats in self.support_extensions.items():
            if path.suffix in formats and path.is_file():
                return type
        return False

    def sample_list(self, to_sample : list, k=6) -> list:
        if (amount:=len(to_sample)) < k:
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

        #print(f"[+]{len(walk)} dirs founds.")

        # add dir to the index
        for idx, dir in enumerate(walk):
            # check if dir was modifiqued
            check = self.find_folder_by_path(dir)
            if check and check['id'] in self.folders:
                if self.compare_mtime(dir.stat(), self.folders[check['id']]['st']):
                    continue 

            # get dir content
            dir_content = filter(self.get_file_type, self.iter(dir))
            files = []
            for file in dir_content:
                id = len(self.files)+1
                self.files[id] = {
                    'path':file
                }
                files.append(id)

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

    def find_file(self, id : int):
        if file:=self.files.get(id):
            return file
        return None 

    def find_folder(self, id: int):
        if folder:=self.folders.get(id):
            return folder 
        return None 

    def find_folder_by_path(self, path : Path):
        for id, dir_path in self.folders.items():
            if path == dir_path['path']:
                return dir_path
        return None
    
    def find_file_by_name(self, string : str):
        """ returns firts coincidence """
        for id, file in self.files.items():
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
            'video':['.mp4', '.avi', '.flv', '.mkv'],
            'music':[],
            'subtitle':['.str', '.vvt']
        }
    def fetch_video_path(self, video_id):
        if video:=self.find_file(video_id):
            return video['path']
        else:
            return False

    def fetch_all_videos(self):
        all = {}
        for id in self.files:
            all[id] = self.fetch_video_info(id)
            del all[id]['id']
        return all

    def fetch_video_from_folder(self, folder_id, video_id):
        """ fetch and process video file info """
        if dir:=self.index[folder_id]:
            files = self.folders[dir]['files']
            if video_id in files:
                return self.fetch_video_info(video_id)
        else:
            return False

    def fetch_thumbnail(self, input_file : Path):
        output_dir = self.root_path.joinpath(self.thumbnails_dir)
        thumb = ffmpegUtils.generate_thumbail(
                                    input_file, 
                                    output_dir.joinpath('thumbs/')
                                    )
        if not thumb:
            return "generic_thumb.png"
        return 'thumbs/'+thumb.name

    def search_video_by_name(self, string : str):
        results =  self.find_file_by_name(string)
        all_coincidences = {}
        for id in results:
            all_coincidences[id] = self.fetch_video_info(id)
        return all_coincidences 
        
        
    def fetch_video_info(self, video_id):
        if video:=self.find_file(video_id):
            file_path = video['path']
            if not video.get('thumb'):
                video['thumb'] = self.fetch_thumbnail(file_path)
            return {
                'id':video_id,
                'title': file_path.stem,
                'thumb': video['thumb'],
                'format':file_path.suffix
            }
        return None

    def fetch_file_sample(self, file_list : list):
        sample = self.sample_list(file_list)
        return [self.fetch_video_info(file) for file in sample]
    
    def fetch_folder(self, id):
        self.update_index()
        if (folder:=self.find_folder(id)) is None:
            return None

        folder_content = map(self.fetch_video_info, folder['files'])

        dict_folder = {
            'id':id,
            'name':folder['name'],
            'files': folder_content,
            'subdirs':{}
        }

        # generate folder preview sample
        for sdir in self.walk_dirs(folder['path']):
            if sdir != folder['path'] and (sub_dir := self.find_folder_by_path(sdir)):
                file_samples = self.sample_list(sub_dir['files']) 
                dict_folder['subdirs'][sub_dir['id']] =  {
                        'name': sub_dir['name'],
                        'file_samples':self.fetch_file_sample(file_samples)
                }

        return dict_folder 

    def fetch_main_preview(self):
        """ get preview of the root dirs """
        self.update_index()
        folders = {}
        for dir in self.get_root_folders():
            folder = self.folders[dir]
            folders[folder['id']] = {
                'name': folder['name'],
                'file_samples':self.fetch_file_sample(folder['files'])
            }
        return folders

if __name__ == '__main__':
   pass

else:
    media_manager = FetchVideo()
    media_manager.root_path = media_manager.root_path.joinpath('fkstreaming')
    media_manager.update_index()
