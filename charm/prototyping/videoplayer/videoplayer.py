import cv2

import arrow
import numpy

import nygame
import pygame
from pygame.surface import Surface


def cv2pg(frame_yx_bgr: numpy.ndarray) -> numpy.ndarray:
    frame_yx_rgb = cv2.cvtColor(frame_yx_bgr, cv2.COLOR_BGR2RGB)
    frame_xy_rgb = frame_yx_rgb.swapaxes(0, 1)
    return frame_xy_rgb


def rescale_frame(frame, scale):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


class VideoPlayer:
    def __init__(self, videopath: str, *, width: int = None):
        self.cap = cv2.VideoCapture(videopath)
        self.frame = None
        self.start_time = arrow.now()

        self.orig_width = self.cap.get(3)
        self.orig_height = self.cap.get(4)

        if width is None:
            width = self.orig_width

        self.scale = width / self.orig_width

        self.size = int(width), int(self.orig_height * self.scale)

        self.image = Surface(self.size)

    def get_frame(self, time: float) -> numpy.ndarray:
        while self.cap.get(cv2.CAP_PROP_POS_MSEC) < time * 1000:
            frame = self.cap.read()[1]
            if frame is None:
                return
            if self.scale != 1:
                frame = rescale_frame(frame, self.scale)
            self.frame = cv2pg(frame)
        return self.frame

    def update(self, time):
        pygame.surfarray.blit_array(self.image, self.get_frame(time))


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (1280, 720), fps = 120, showfps = True, bgcolor="pink")
        self.videoplayer = VideoPlayer("C:/Users/digid/Videos/Awoken.mp4")

    def render_video(self, time: float):
        pygame.surfarray.blit_array(self.surface, self.videoplayer.get_frame(time))

    def loop(self, events):
        now = arrow.now()
        time = (now - self.videoplayer.start_time).total_seconds()
        self.render_video(time)


# Game().run()
