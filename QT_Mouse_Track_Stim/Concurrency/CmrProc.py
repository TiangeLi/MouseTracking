# coding=utf-8

"""Camera Process"""

import sys
import cv2
import time
from Misc.GlobalVars import VID_DIM
import flycapture2a as fc
from Misc.GlobalVars import *
from Misc.CustomClasses import *
import threading as thr
if sys.version[0] == '2':
    import Queue as Queue
else:
    import queue as Queue


# todo: separate main thread and child thread variables. delineate read and write only
class CameraDevice(fc.Context):
    """Container for PTGrey FireFly Camera Hardware"""
    def __init__(self):
        self.running = False
        self.in_use = False
        self.cmr_err = fc.ApiError
        self.get_img = self.tempImgGet
        self.connect_camera()

    def connect_camera(self):
        """Initializes a PTGrey FireFly Camera"""
        try:
            self.connect(*self.get_camera_from_index(0))
            self.set_video_mode_and_frame_rate(fc.VIDEOMODE_640x480Y8, fc.FRAMERATE_30)
            self.set_property(**self.get_property(fc.FRAME_RATE))
            self.start_capture()
        except self.cmr_err:
            self.running = False
        else:
            self.running = True

    def close_camera(self):
        """Closes Device and Exits Process"""
        self.running = False
        try:
            self.stop_capture()
            self.disconnect()
        except self.cmr_err:
            pass


class VideoSource(object):
    """Instead of using the camera, we can also load an already recorded video"""
    def __init__(self):
        self.video = None
        self.get_img = None

    def assign_video(self, vidpath):
        """Creates a new video read object from source video"""
        self.video = cv2.VideoCapture(vidpath)
        iterator = self.img_iterator()
        self.get_img = lambda: next(iterator)

    def img_iterator(self):
        """Creates a generator for getting the next frame"""
        _, frame = self.video.read()
        while frame is not None:
            base = np.zeros(VID_DIM, dtype='uint8')
            frame = frame[..., 1] if len(frame.shape) == 3 else frame
            base[:frame.shape[0], :frame.shape[1]] = frame
            yield base
            time.sleep(15.0 / 1000.0)
            _, frame = self.video.read()


class CameraHandler(StoppableProcess):
    """Camera Process that handles incoming messages and relays them to camera hardware"""
    def __init__(self, cmr_cv2_mp_array):
        super(CameraHandler, self).__init__()
        self.name = PROC_CMR
        self.connected = True
        self.input_msgs = mp.Queue()
        self.output_msgs = PROC_HANDLER_QUEUE
        self.cmr_cv2_mp_array = cmr_cv2_mp_array
        self.rec_to_file_sync_event = mp.Event()
        # Sometimes, we need to tell CV2_Proc To calibrate a new background
        self.get_background = False

    def run(self):
        """This is called by self.start(), and creates a new process"""
        self.init_unpickleable_objs()
        # Threading
        POLLING = 'polling'
        thr_msg_polling = thr.Thread(target=self.msg_polling, name=POLLING, daemon=True)
        thr_msg_polling.start()
        # We begin by using camera; vidpath=None activates Camera functions
        self.toggle_vid_src(vidpath=None)
        if not self.camera.running:
            self.report_camera_error()
        # Main Camera Loop
        while self.connected:
            # Attempt to connect to camera if not connected but we use it as vidsrc
            if not self.camera.running and self.camera.in_use:
                time.sleep(500.0 / 1000.0)
                self.camera.connect_camera()
                continue
            # Get Frames (main function of loop)
            self.get_frames()
            # Sometimes we may need to get new frames
            if self.get_background:  # this is True iff all getimg methods have been switched to new ones
                self.get_background = False
                self.get_frames()  # Therefore, this get_frames() will acquire an image with new vidsrc
                self.msg_proc_handler(cmd=CMD_GET_BG)  # cv2 will acquire bg using only new vidsrc images
            # Check if exiting process
            if self.stopped():
                self.connected = False
                self.camera.close_camera()
                while True:
                    time.sleep(5.0 / 1000.0)
                    threads = [thread.name for thread in thr.enumerate()]
                    if POLLING not in threads:
                        break  # we only exit process if all child threads were terminated
        print('Exiting Camera Process...')

    # Msging Protocol
    def setup_msg_parser(self):
        """Dictionary of {Msg:Actions}"""
        self.msg_parser = {
            CMD_EXIT: lambda val: self.stop(),
            CMD_SET_VIDSRC: lambda val: self.toggle_vid_src(val)
        }

    def msg_proc_handler(self, cmd, val=None):
        """Sends a message to process handler"""
        msg = NewMessage(dev=self.name, cmd=cmd, val=val)
        self.output_msgs.put_nowait(msg)

    def msg_polling(self):
        """Run on separate thread. Listens to input_msgs queue for messages"""
        while self.connected:
            try:
                msg = self.input_msgs.get(timeout=0.5)
            except Queue.Empty:
                time.sleep(30.0 / 1000.0)
            else:
                msg = ReadMessage(msg)
                self.process_message(msg)

    def process_message(self, msg):
        """Follows instructions in queue message"""
        self.msg_parser[msg.command](msg.value)

    # Concurrency
    def init_unpickleable_objs(self):
        """Sets up objects that must be initialized in the process it will be running"""
        self.camera = CameraDevice()
        self.vidsrc = VideoSource()
        self.cmr_cv2_np_array = self.cmr_cv2_mp_array.generate_np_array()
        self.setup_msg_parser()

    def toggle_vid_src(self, vidpath):
        """Switch between using camera and a video file"""
        if not vidpath:  # use camera
            self.camera.in_use = True
            self.next_frame = self.camera.get_img
            self.error = self.camera.cmr_err
        elif vidpath:  # use supplied video
            self.camera.in_use = False
            self.vidsrc.assign_video(vidpath)
            self.next_frame = self.vidsrc.get_img
            self.error = StopIteration
        self.get_background = True

    def get_frames(self):
        """Acquires 1 Image per call"""
        if self.cmr_cv2_np_array.can_send_img():
            try:
                data = self.next_frame()
            except self.error:
                if self.error == self.camera.cmr_err:
                    self.report_camera_error()
                elif self.error == StopIteration:
                    time.sleep(0.10)
            else:
                self.cmr_cv2_np_array.send_img(data)
                self.cmr_cv2_np_array.set_can_recv_img()
                # Inform CmrVidRecProcess that it can record a frame
                self.rec_to_file_sync_event.set()
        else:
            time.sleep(1.0 / 1000.0)

    def report_camera_error(self):
        """If camera reports an error, we notify proc_handler"""
        self.camera.running = False
        self.camera.close_camera()
        destination = PROC_CV2
        self.msg_proc_handler(cmd=MSG_ERROR, val=destination)
