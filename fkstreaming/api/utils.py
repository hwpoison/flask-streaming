import webvtt
import random
from pathlib import Path
import ffmpeg
from ffprobe import FFProbe
"""
webvtt = webvtt.from_srt('videos/sub.srt')
webvtt.save()
"""

default_dirs = ['videos', 'C:\\Users\\Guille\\Desktop\\videos']

class GetVideos():
	def __init__(self):
		self.ROOT_PATH = Path("../")
		self.VIDEO_DIR  = 'videos'
		self.THUMBS_DIR = 'videos/thumbs'

	def update(self):
		#self.THUMBS_DIR = f'{self.ROOT_PATH}thumbs/'
		pass

	def filter_extension(self, entry):
		extensions = {
			'video':['.mp4','.avi', '.flv'],
			'music':['.mp3'],
			'subtitle':['.str','.vvt']
		}
		for type, formats in extensions.items():
			if entry.suffix in formats:
				return type, entry

	def get_files(self, path=None): 
		if not path:
			path = self.ROOT_PATH.joinpath(self.VIDEO_DIR)
		found = {
			'path': path,
			'files': {}
		}
		# scan files in path and return name and filetypes
		for entry in path.iterdir():
			if entry.is_file() and (file_info:=self.filter_extension(entry)):
				if not found['files'].get(file_info[0]):
					found['files'][file_info[0]] = []
				
				found['files'][file_info[0]].append(file_info[1])
		return found

	def generate_thumbail(self, file_path):
		thumbs_path = self.ROOT_PATH.joinpath(self.THUMBS_DIR)
		thumbnail_name = f'{file_path.stem}_thumb.jpg'
		thumb_full_path = thumbs_path.joinpath(thumbnail_name)
		# first, check if thumbils actual exists
		if Path(thumbs_path.joinpath(thumbnail_name)).exists():
			return thumbnail_name

		# now generate video thumbail form random frame
		print(f'[+]Generating thumbail for {file_path}')
		probe = self.get_video_probe(file_path)
		duration = probe['format']['duration']
		rtime = random.randint(0, int(float(duration))//2)
		try:
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
			return 'generic_thumb.jpg'

	def get_video_probe(self, filename):
		probe = ffmpeg.probe(filename)
		return probe

	def get_videos(self):
		videos = {}
		files =  self.get_files()
		if not files['files']:
			return {}		
		path = files['path']
		for id, file in enumerate(files['files']['video']):
			videos[id] = {
				'id': id,
				'name':file.name,
				'stream':str(file),
				'thumb':self.generate_thumbail(path.joinpath(file.name))
			}
		return videos


if __name__ == '__main__':
	gett = GetVideos()
	#gett.ROOT_PATH = "../videos/"
	gett.update()
	v = gett.get_videos()
	print(v)
	
	"""pwd = Path('../videos')
	for e in pwd.iterdir():
		print(e.suffix)
"""
else:
	file_manage = GetVideos()
	file_manage.ROOT_PATH = Path('./fkstreaming/')

