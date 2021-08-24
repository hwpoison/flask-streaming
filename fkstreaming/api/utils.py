import random
import configparser

import ffmpeg
import webvtt
from ffprobe import FFProbe
from pathlib import Path
"""
webvtt = webvtt.from_srt('videos/sub.srt')
webvtt.save()
"""
config = configparser.ConfigParser()

class MediaFileManager():
	""" Media file Manager	
		A set of methods to scan dirs and get specific files types
	"""
	def __init__(self):
		self.ROOT_PATH = Path.cwd().joinpath('fkstreaming')
		self.VIDEO_DIR  = 'videos'
		self.THUMBS_DIR = 'videos/thumbs'
		self.support_extensions = {
			'video':['.mp4', '.avi', '.flv', '.mkv'],
			'music':['.mp3'],
			'subtitle':['.str', '.vvt']
		}
		self.index = {

		}

	def get_dir_from_config(self):
		""" parse config file 'dirs.ini' with user custom dirs """
		try:
			config.read(self.ROOT_PATH.joinpath('videos/dirs.ini'))
			return [Path(dir) for dir in config['PATHS']['video_dirs'].split('\n')]
		except configparser.ParsingError:
			raise Exception("Error to parsing 'dirs.ini' file configuration, please check it!")
	
	def filter_file_type(self, path):
		""" This function clasify and filter entries by format extension """
		for type, formats in self.support_extensions.items():
			if path.suffix in formats:
				return type
		return False
	
	def get_video_probe(self, video_path):
		""" Returns video probe """
		probe = ffmpeg.probe(video_path)
		return probe

	def generate_thumbail(self, file_path):
		""" takes a video path and generate and save a thumbnail """ 

		thumbs_path = self.ROOT_PATH.joinpath(self.THUMBS_DIR)
		thumbnail_name = f'{file_path.stem}_thumb.jpg'
		thumb_full_path = thumbs_path.joinpath(thumbnail_name)
		# first, check if thumbils actual exists
		if Path(thumbs_path.joinpath(thumbnail_name)).exists():
			return thumbnail_name

		# now generate video thumbail form random frame
		try:
			print(f'[+]Generating thumbail for {file_path}')
			probe = self.get_video_probe(file_path)
			duration = probe['format']['duration']
			rtime = random.randint(0, int(float(duration))//2)
			(
			    ffmpeg
			    .input(file_path, ss=rtime)
			    .filter('scale', 500, -1)
			    .output(str(thumb_full_path), vframes=1) # agregar generador nombre
			    .overwrite_output()
			    .global_args("-nostats")
			    .run()
			)
			return thumbnail_name#out_name
		except:
			return 'generic_thumb.png'

	def walk_dir(self, path):
		return path.glob("**/") # walk into dir and get subdirs

	def update_index(self): # get all dirs
		self.index = {}
		root_dirs = self.get_dir_from_config()
		all_dirs = []
		# scan all dirs
		for dir in root_dirs:
			all_dirs.extend(list(dir.glob('**/')))

		# add dir to the index
		for idx, dir in enumerate(all_dirs):
			is_root = True if dir in root_dirs else False
			# get dir files
			files = {}
			dir_content = filter(self.filter_file_type, dir.iterdir())
			# folder info
			self.index[dir] = {
					'id': idx,
					'name': dir.name,
					'files': files,
					'root_dir': is_root
			}
			# folder content
			for file_id, file in enumerate(dir_content):
				files[file_id] = {
						'id':file_id,
						'thumb': self.generate_thumbail(file),
						'title': file.stem,
						'file_path': str(file.parent),
						'file_name': file.name,
				}

		return True 

	def fetch_root_folders(self):
		""" fetch root folders """
		self.update_index()
		for path, info in self.index.items():
			if info['root_dir'] is True:
				yield path	

	def get_folder_path(self, id):
		for dir, info in self.index.items():
			if id == info['id']:
				return dir  
		return False

	def fetch_folder_by_id(self, id):
		path = self.get_folder_path(id)
		if path:
			return path
		else:
			return False

	def fetch_folder(self, folder_id):
		path = self.fetch_folder_by_id(folder_id)
		folder_index = self.index[path]
		folder = {
			'name':folder_index['name'],
			'id':folder_index['id'],
			'files':folder_index['files'],
			'subdirs':{}
		}
		for dir in self.walk_dir(path):
			dir_idx = self.index[dir]
			if dir != path:
				folder['subdirs'][dir_idx['id']] =  {
						'name': dir_idx['name'],
						'file_samples':self.sample_dict(dir_idx['files'])
						}
		return folder 

	def sample_dict(self, to_sample, k=5):
			if (amount:=len(to_sample)) < k:
				k = amount
			sample = random.sample(list(to_sample), k)
			return [to_sample[i] for i in sample]

	def fetch_main_preview(self):
		""" get preview of the root dirs """
		folders = {}
		for dir in self.fetch_root_folders():
			folder = self.index[dir]
			folders[folder['id']] = {
				'name': folder['name'],
				'file_samples':self.sample_dict(folder['files'])
				
			}
		return folders

	def fetch_video_info(self, folder_id, video_id):
		if dir:=self.get_folder_path(folder_id):
			folder = self.index[dir]
			if video:=folder['files'].get(video_id):
				video['id_folder'] = folder['id']
				return video 
		else:
			return False

	def fetch_video(self, folder_id, video_id):
		if dir:=self.get_folder_path(folder_id):
			folder = self.index[dir]
			if video:=folder['files'].get(video_id):
				video['id_folder'] = folder['id']
				return {
					'file_name':str(video['file_name']),
					'file_path':str(video['file_path']),
					'thumb':str(video['thumb'])
				}
		else:
			return False

if __name__ == '__main__':
	get = MediaFileManager()
	get.ROOT_PATH = Path("../")
	get.update_index()
	files = get.index
	print(files)
else:
	file_manage = MediaFileManager()
	file_manage.update_index()