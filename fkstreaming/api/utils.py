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

	def get_dir_from_config(self):
		""" parse config file 'dirs.ini' with user custom dirs """
		try:
			config.read(self.ROOT_PATH.joinpath('videos/dirs.ini'))
			return [Path(dir) for dir in config['PATHS']['video_dirs'].split('\n')]
		except configparser.ParsingError:
			raise Exception("Error to parsing 'dirs.ini' file configuration, please check it!")

	def scan_dirs(self, dirs_list):
		""" Scan all files in the path list """
		all_files = []
		default_dirs = map(Path, dirs_list)
		for files in default_dirs:
			all_files.extend(files.glob("**/*.*"))
		return all_files

	def classify_files(self, files_paths):
		""" Classify and sumarize files by format extension """ 
		found = {}
		for file_path in files_paths:
			type = self.detect_file_type(file_path.suffix)
			if not found.get(type):
				found[type] = []
			found[type].append(file_path)
		return found
	
	def detect_file_type(self, suffix):
		""" This function clasify and filter entries by format extension """
		for type, formats in self.support_extensions.items():
			if suffix in formats:
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

	def get_files_by_type(self, type='video'):
		""" fetches all files of certain media type """
		videos = {}
		files =  self.classify_files(
			self.scan_dirs(self.get_dir_from_config())
		)
		if not files.get(type):
			return {}
		for id, file in enumerate(files[type]):
			videos[id] = {
				'id': id,
				'title':str(file.stem),
				'file_name':str(file.name),
				'file_path':str(file.parent),
				'file_type':str(file.suffix),
				'thumb':self.generate_thumbail(file)
			}
		return videos

if __name__ == '__main__':
	gett = MediaFileManager()
	gett.ROOT_PATH = Path("../")
	print(gett.get_files_by_type())
else:
	file_manage = MediaFileManager()
	

