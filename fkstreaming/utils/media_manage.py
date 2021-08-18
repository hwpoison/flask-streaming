import random
import configparser
import time
import ffmpeg
import webvtt
from ffprobe import FFProbe
from pathlib import Path

"""
webvtt = webvtt.from_srt('videos/sub.srt')
webvtt.save()
"""
config = configparser.ConfigParser()

class MediaManager():
	""" Media file Manager	
		A set of methods to scan dirs and get specific files types
	"""
	def __init__(self):
		self.root_path = Path.cwd()
		self.config_file = 'dirs.ini'
		self.thumbnails_dir = 'thumbnails/'
		self.support_extensions = {
			'video':['.mp4', '.avi', '.flv', '.mkv'],
			'music':['.mp3'],
			'subtitle':['.str', '.vvt']
		}
		self.index = {}
		self.dirs = {}
		self.files = {}

	def load_config_file(self):
		""" parse config file 'dirs.ini' with user custom dirs """
		try:
			config.read(self.root_path.joinpath(self.config_file))
			print(self.root_path.joinpath(self.config_file))
			return [Path(dir) for dir in config['DIRS']['video_dirs'].split('\n')]
		except configparser.ParsingError:
			raise Exception("Error to parsing 'dirs.ini' file configuration, please check it!")
	
	
	def generate_thumbail(self, input_file):
		""" takes a video path and generate and save a thumbnail """ 
		thumbs_path = self.root_path.joinpath(self.thumbnails_dir)
		thumbnail_name = f'{input_file.stem}_thumb.jpg'
		thumb_full_path = thumbs_path.joinpath(thumbnail_name)
		# first, check if thumbils actual exists
		if Path(thumbs_path.joinpath(thumbnail_name)).exists():
			return thumbnail_name

		# now generate video thumbail form random frame
		try:

			probe = ffmpeg.probe(input_file)
			print(probe)
			duration = probe['format']['duration']
			rtime = random.randint(0, int(float(duration))//2)
			print(f'[+]Generating thumbail for {input_file}')
			(
			    ffmpeg
			    .input(input_file, ss=rtime)
			    .filter('scale', 500, -1)
			    .output(str(thumb_full_path), vframes=1) # agregar generador nombre
			    .overwrite_output()
			    .run()
			)
			return thumbnail_name#out_name
		except:
			return 'generic_thumb.png'
	
	def get_file_type(self, path):
		""" This function clasify and filter entries by format extension """
		for type, formats in self.support_extensions.items():
			if path.suffix in formats and path.is_file():
				return type
		return False

	def walk_dir(self, path):
		return path.glob("**/") # walk into dir and get subdirs
	
	def sample_list(self, to_sample, k=5):
			if (amount:=len(to_sample)) < k:
				k = amount
			sample = random.sample(to_sample, k)
			return sample
	
	def update_index(self): # get all dirs
		root_dirs = self.load_config_file()
		if len(root_dirs) == 1:
			self.dirs = {}
			
		all_dirs = []
		print("[+]Updating Index")
		# scan all dirs
		for dir in root_dirs:
			all_dirs.extend(list(dir.glob('**/')))
		print(f"[+]{len(all_dirs)} dirs founds.")
		# add dir to the index
		for idx, dir in enumerate(all_dirs):
			# check if dir was modify
			if dir in self.dirs:
				last_mtime = self.dirs[dir]['st'].st_mtime
				actual_mtime = dir.stat().st_mtime
				if last_mtime == actual_mtime:
					continue
			is_root = True if dir in root_dirs else False

			# get dir content
			dir_content = filter(self.get_file_type, dir.iterdir())
			files = []
			for file in dir_content:
				id = len(self.files)+1
				self.files[id] = {
					'path':file
				}
				files.append(id)
			if len(files) > 0:
				# set folder info
				self.dirs[dir] = {
						'id': idx,
						'name': dir.name,
						'files': files,
						'is_root': is_root,
						'st':  dir.stat()
				}
				self.index[idx] = dir

		return True 

	def get_root_folders(self):
		""" fetch only root folders (from dirs.ini)"""
		self.update_index()
		for path, info in self.dirs.items():
			if info['is_root'] is True:
				yield path	
	
	def get_main_preview(self):
		""" get preview of the root dirs """
		self.update_index()
		folders = {}
		for dir in self.get_root_folders():
			folder = self.dirs[dir]
			folders[folder['id']] = {
				'name': folder['name'],
				'file_samples':self.get_file_sample(folder['files'])
			}
		return folders

	def get_file_sample(self, file_list):
		sample = self.sample_list(file_list)
		return [self.get_video_info(file) for file in sample]
	
	def get_folder(self, folder_id):
		self.update_index()
		if path:=self.index.get(folder_id):
			dir = self.dirs[path]
		else:
			return False
		folder = {
			'id':folder_id,
			'name':dir['name'],
			'files':[self.get_video_info(file) for file in dir['files']],
			'subdirs':{}
		}
		# generate folder preview sample
		for sdir in self.walk_dir(path):
			if sdir != path and sdir in self.dirs:
				dir_idx = self.dirs[sdir]
				file_samples = self.sample_list(dir_idx['files']) 
				folder['subdirs'][dir_idx['id']] =  {
						'name': dir_idx['name'],
						'file_samples':self.get_file_sample(file_samples)
				}
		return folder 

	def get_video_info(self, video_id):
		if video:=self.files.get(video_id):
			path = video['path']
			if not video.get('thumb'):
				#add only if not exists
				video['thumb'] = self.generate_thumbail(path)
			return {
				'id':video_id,
				'title': path.stem,
				'thumb': video['thumb'],
				'format':path.suffix
			}

	def get_video_from_folder(self, folder_id, video_id):
		""" get and process video file info """
		if dir:=self.index[folder_id]:
			files = self.dirs[dir]['files']
			if video_id in files:
				return self.get_video_info(video_id)
		else:
			return False

	def get_video_path(self, video_id):
		""" fetch file path for download """
		if video:=self.files.get(video_id):
			return video['path']
		else:
			return False

	def get_all_videos(self):
		all = {}
		for id in self.files:
			all[id] = self.get_video_info(id)
			del all[id]['id']
		return all

if __name__ == '__main__':
	get = MediaManager()
else:
	media_manager = MediaManager()
	media_manager.root_path = media_manager.root_path.joinpath('fkstreaming')
	media_manager.update_index()