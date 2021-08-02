import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size
import sys, datetime
from threading import Thread
import re
buffer_dir = '../fkstreaming/videos/poll/'
videos_dir = '../fkstreaming/videos/'


def monitor(ffmpeg, duration, time_, time_left, process):
    """
    Handling proccess.

    Examples:
    1. Logging or printing ffmpeg command
    logging.info(ffmpeg) or print(ffmpeg)

    2. Handling Process object
    if "something happened":
        process.terminate()

    3. Email someone to inform about the time of finishing process
    if time_left > 3600 and not already_send:  # if it takes more than one hour and you have not emailed them already
        ready_time = time_left + time.time()
        Email.send(
            email='someone@somedomain.com',
            subject='Your video will be ready by %s' % datetime.timedelta(seconds=ready_time),
            message='Your video takes more than %s hour(s) ...' % round(time_left / 3600)
        )
       already_send = True

    4. Create a socket connection and show a progress bar(or other parameters) to your users
    Socket.broadcast(
        address=127.0.0.1
        port=5050
        data={
            percentage = per,
            time_left = datetime.timedelta(seconds=int(time_left))
        }
    )

    :param ffmpeg: ffmpeg command line
    :param duration: duration of the video
    :param time_: current time of transcoded video
    :param time_left: seconds left to finish the video process
    :param process: subprocess object
    :return: None
    """
    per = round(time_ / duration * 100)
    sys.stdout.write(
        "\rTranscoding...(%s%%) %s left [%s%s]" %
        (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
    )
    sys.stdout.flush()



def encodeVideo(file_name):
	print(f'Starting encoding for {file_name}')
	video = ffmpeg_streaming.input(f'{videos_dir}{file_name}')
	hls = video.hls(Formats.h264())
	hls.auto_generate_representations([480])
	hls.output(f"{buffer_dir}{file_name}", monitor=monitor)

def find_video():
	# find video in database
	return "cap1.mp4"

def get_stream_file(video_name):
	print(f"Getting video stream for {video_name}")
	video_name = find_video() 

	if not video_name:
		return 0
	try:
		video_stream = Thread(target=encodeVideo, name="video", args=(video_name,))
		video_stream.start()	
	except:
		print(f'Video File \"{video_name}\" not found!')
		return False
	print(f"Ready!")
	file_name = re.findall("(.*)\.[a-z0-9]{3}$", video_name)
	info =  {'dir':buffer_dir, 'path':file_name[0] + '.m3u8'}
	print(info)
	return info
