import cv2

import arrow

import nygame
import pygame


def cv2pg(frame_yx_bgr):
    frame_yx_rgb = cv2.cvtColor(frame_yx_bgr, cv2.COLOR_BGR2RGB)
    frame_xy_rgb = frame_yx_rgb.swapaxes(0, 1)
    return frame_xy_rgb


class VideoPlayer:
    def __init__(self, videopath):
        self.cap = cv2.VideoCapture(videopath)
        self.frame = None
        self.start_time = arrow.now()

    def get_frame(self, time):
        while self.cap.get(cv2.CAP_PROP_POS_MSEC) < time * 1000:
            self.frame = cv2pg(self.cap.read()[1])
        return self.frame


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (1280, 720), fps = 120, showfps = True, bgcolor="pink")
        self.videoplayer = VideoPlayer("C:/Users/digid/Videos/Awoken.mp4")

    def render_video(self, time):
        pygame.surfarray.blit_array(self.surface, self.videoplayer.get_frame(time))

    def loop(self, events):
        now = arrow.now()
        time = (now - self.videoplayer.start_time).total_seconds()
        self.render_video(time)


Game().run()
