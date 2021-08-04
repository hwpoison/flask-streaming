import webvtt
import random
from pathlib import Path
import ffmpeg
from ffprobe import FFProbe
"""
webvtt = webvtt.from_srt('videos/sub.srt')
webvtt.save()
"""

class GetVideos():
	def __init__(self):
		self.ROOT_PATH = Path.cwd().joinpath('fkstreaming')
		self.VIDEO_DIR  = 'videos'
		self.THUMBS_DIR = 'videos/thumbs'

		self.user_dirs = [
				self.ROOT_PATH.joinpath(self.VIDEO_DIR),
		 		'C:\\Users\\Guille\\Desktop\\videos',
		 		'C:\\Users\\Guille\\Desktop\\downloads\\Los Simpsons\\Temporada 07'
		] 

	def update(self):
		#self.THUMBS_DIR = f'{self.ROOT_PATH}thumbs/'
		pass

	def detect_file_type(self, entry):
		extensions = {
			'video':['.mp4','.avi', '.flv'],
			'music':['.mp3'],
			'subtitle':['.str','.vvt']
		}
		for type, formats in extensions.items():
			if entry.suffix in formats:
				return type
		return False

	def get_dir_files(self):
		all_files = []
		default_dirs = map(Path, self.user_dirs)
		for files in default_dirs:
			all_files.extend(files.glob("**/*.*"))
		return all_files

	def scan_dirs(self, path=None): 
		found = {

		}
		all_files = self.get_dir_files()
		for file_path in all_files:
			type = self.detect_file_type(file_path)
			if not found.get(type):
				found[type] = []
			found[type].append(file_path)
		return found

	def generate_thumbail(self, file_path):
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

	def get_video_probe(self, filename):
		probe = ffmpeg.probe(filename)
		return probe

	def get_videos(self):
		videos = {}
		files =  self.scan_dirs()
		if not files.get('video'):
			return {}
		for id, file in enumerate(files['video']):
			videos[id] = {
				'id': id,
				'file_name':str(file.name),
				'file_path':str(file.parent),
				'thumb':self.generate_thumbail(file)
			}
		return videos


if __name__ == '__main__':
	gett = GetVideos()
	gett.ROOT_PATH = Path("../")
else:
	file_manage = GetVideos()
	

