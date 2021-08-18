import sys, datetime, random
from threading import Thread
from pathlib import Path

import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size


buffer_dir = 'buffer/'

class encodeThread(Thread):
    def __init__(self, file_path : Path, temp_dir : Path, name : str):
        Thread.__init__(self, target=self.encodeVideo, name=name)
        self.file_path = file_path
        self.file_name = name
        self.temp_dir = temp_dir
        self.interrupt = False
        self.print_monitor = True
        self.default_size = ['24p','144p', '360p']
        self.sizes = {
                '24p':  Representation(Size(16, 24), Bitrate(25 * 1024, 9 * 1024)),
                '48p':  Representation(Size(32, 48), Bitrate(55 * 1024, 15 * 1024)),
                '96p':  Representation(Size(64, 96), Bitrate(95 * 1024, 30 * 1024)),
                '120p': Representation(Size(160, 120), Bitrate(40 * 1024, 30 * 1024)),
                '144p': Representation(Size(256, 144), Bitrate(95 * 1024, 64 * 1024)),
                '240p': Representation(Size(426, 240), Bitrate(150 * 1024, 94 * 1024)),
                '360p': Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024)),
                '480p': Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024)),
                '720p': Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024)),
                '1080p':Representation(Size(1920, 1080), Bitrate(4096 * 1024, 320 * 1024)),
                '2k':   Representation(Size(2560, 1440), Bitrate(6144 * 1024, 320 * 1024)),
                '4k':   Representation(Size(3840, 2160), Bitrate(17408 * 1024, 320 * 1024))
        }

    def monitor(self, ffmpeg, duration, time_, time_left, process):
        if self.interrupt:
            process.kill()
        if self.print_monitor:
            per = round(time_ / duration * 100)
            sys.stdout.write(
                "\rTranscoding...(%s%%) %s left [%s%s]" %
                (per, datetime.timedelta(seconds=int(time_left)), '#' * per, '-' * (100 - per))
            )
            sys.stdout.flush()

    def encodeVideo(self):
        print(f'Starting encoding for {self.file_path}\n')
        video = ffmpeg_streaming.input(str(self.file_path))
        hls = video.hls(Formats.h264()) #h264
        #hls.flags("delete_segments")
        hls.representations(*(self.sizes[size] for size in self.default_size))
        try:
            output_path = self.temp_dir.joinpath(self.file_name)
            hls.output(output_path, monitor=self.monitor)
        except:
            print("Finished?")

    def finish(self):
        if self.interrupt is False:
            self.interrupt = True

    def start_coding(self):
        self.start()


class ThreadManager():
    def __init__(self):
        self.poll = {}
        self.work_path = Path.cwd() 

    def new(self, file_path, id):
        file_name = file_path.stem.replace('.',' ')
        manifest_filename = self.work_path.joinpath(file_name + '.m3u8')
        if id not in self.poll:
            new_thread = encodeThread(file_path, self.work_path, name=file_name)
            new_thread.start_coding()
            self.poll[id] = new_thread # register thread
        return manifest_filename

    def kill_all(self):
        for name, thread in self.poll.items():
            if thread.is_alive():
                print("finishing ", name)
                thread.finish() 
        self.poll = {}

    def finish(self, id):
        if thread:=self.poll.get(id):
            thread.finish()
            print(thread, " killed")
            del self.poll[id]
            return True
        return False

if __name__ == '__main__':
    transcode_manager = ThreadManager()
else:
    transcode_manager = ThreadManager()
    transcode_manager.work_path = Path.cwd().joinpath('fkstreaming/stream/buffer')