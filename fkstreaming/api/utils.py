import webvtt
import os, re
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
		self.ROOT_FOLDER = "fkstreaming/videos/"
		self.THUMBS_DIR = f'fkstreaming/videos/thumbs/'

	def update(self):
		self.THUMBS_DIR = f'{self.ROOT_FOLDER}thumbs/'

	def filter_extension(self, entry):
		extensions = {
			'video':['mp4','avi', 'flv'],
			'music':['mp3'],
			'subtitle':['str','vvt']
		}
		for type, formats in extensions.items():
			pattern = '|'.join(formats)
			c = re.match("([a-zA-Z0-9].+)\.[%s]{3}$"%pattern, entry)
			if c:
				return type, c.string

	def get_files(self): 
		# scan files in path and return name and filetypes
		entries = Path(self.ROOT_FOLDER)
		found = {
			'path': self.ROOT_FOLDER,
			'files': {}
		}
		for entry in entries.iterdir():
			if entry.is_file() and (file_info:=self.filter_extension(entry.name)):
				if not found['files'].get(file_info[0]):
					found['files'][file_info[0]] = []
				found['files'][file_info[0]].append(file_info[1])
		return found

	def extract_filename(self, file_name):
		filename =  re.findall(".+/(.+)\..{3}$", file_name)
		if filename:
			return filename[0] 
		else:
			return False

	def generate_thumbail(self, in_file):
		# first, check if thumbils actual exists
		file_name = self.extract_filename(in_file)
		file_name = f"{file_name}_thumb.jpg"
		out_name = f"{self.THUMBS_DIR}{file_name}"
		if os.path.exists(out_name):
			return file_name

		# now generate video thumbail form random frame
		print(f"[+]Generating thumbail for {in_file}")
		try:
			probe = self.get_video_probe(in_file)
			duration = probe['format']['duration']
			rtime = random.randint(0, int(float(duration))//2)
			(
			    ffmpeg
			    .input(in_file, ss=rtime)
			    .filter('scale', 500, -1)
			    .output(out_name, vframes=1) # agregar generador nombre
			    .overwrite_output()
			    .global_args("-nostats")
			    .run()
			)
			return file_name#out_name
		except:
			return 'generic_thumb.jpg'

	def get_video_probe(self, filename):
		probe = ffmpeg.probe(filename)
		return probe

	def get_videos(self):
		videos = {
				#1 : { 'name':string , 'thumb':stringpath}	
		}
		files =  self.get_files()
		if not files['files']:
			return {}
			
		path = files['path']
		for id, video_name in enumerate(files['files']['video']):
			videos[id] = {
				'id': id,
				'name':video_name,
				'stream':video_name,
				'thumb':self.generate_thumbail(path+video_name)
			}
		return videos


if __name__ == '__main__':
	gett = GetVideos()
	gett.ROOT_FOLDER = "../videos/"
	gett.update()
	gett.get_videos()
else:
	file_manage = GetVideos()

