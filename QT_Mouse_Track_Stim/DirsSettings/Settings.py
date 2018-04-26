# coding=utf-8

"""Handles IO and Configurations across all modules and devices"""

import sys
import numpy as np
from Misc.GlobalVars import *


class MainSettings(object):
    """Holds all relevant user configurable settings"""
    def __init__(self):
        # Last Used Settings
        self.last_save_dir = ''
        self.ttl_time = 0.0
        # target area settings (areas that mouse will receive stimulation if within)
        self.target_area_radius = 30
        self.last_targ_areas = None
        self.target_areas = {}
        self.last_quadrant = BOTTOMLEFT
        self.bounding_coords = DEFAULT_BOUNDS

    def load_examples(self):
        """Example settings for first time users"""
        self.last_save_dir = HOME_DIR + '\\Desktop\\MouseTracking'
        self.ttl_time = 300.0  # in secs; 5min Default
        self.last_targ_areas = TargetAreas()


class TargetAreas(object):
    """A group of target regions"""
    def __init__(self):
        self.areas = []
        self.generate_targ_areas(check_radius=False)

    def generate_targ_areas(self, check_radius, dirs=None):
        """Randomly sample num points from a 2D normal"""
        areas = []
        num_to_sample = 5
        if check_radius:
            x1, y1 = dirs.settings.bounding_coords[0]
            x2, y2 = dirs.settings.bounding_coords[1]
            xmid = (x1 + x2) / 2
            ymid = (y1 + y2) / 2
            quadrant_selector = {
                TOPLEFT: (x1, y1, xmid, ymid),
                TOPRIGHT: (xmid, y1, x2, ymid),
                BOTTOMLEFT: (x1, ymid, xmid, y2),
                BOTTOMRIGHT: (xmid, ymid, x2, y2),
            }
            x1, y1, x2, y2 = quadrant_selector[dirs.settings.last_quadrant]
        while len(areas) < num_to_sample:
            loc = np.random.multivariate_normal((0.5, 0.5), (((0.5/3)**2, 0), (0, (0.5/3)**2)), size=1)[0]
            use = True
            if check_radius:
                xscale = x2 - x1
                xshift = x1
                yscale = y2 - y1
                yshift = y1
                x = int((loc[0] * xscale) + xshift)
                y = int((loc[1] * yscale) + yshift)
                for area in areas:
                    cx = int((area.x * xscale) + xshift)
                    cy = int((area.y * yscale) + yshift)
                    if ((x-cx)**2 + (y-cy)**2) <= dirs.settings.target_area_radius ** 2:
                        use = False
            if use:
                if 0 <= loc[0] <= 1 and 0 <= loc[1] <= 1:
                    areas.append(SingleTargetArea(x=loc[0], y=loc[1], area_id=len(areas)))
        self.areas = areas


class SingleTargetArea(object):
    """A single target region"""
    def __init__(self, x, y, area_id=None, tested=False):
        self.x = x
        self.y = y
        self.area_id = area_id
        self.tested = tested
