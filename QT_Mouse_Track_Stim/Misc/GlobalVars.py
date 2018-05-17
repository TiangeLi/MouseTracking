# coding=utf-8

"""Common Variables/Names used across modules"""

import os
from PyCapture2 import FRAMERATE
import PyQt4.QtGui as qg
import PyQt4.QtCore as qc
import multiprocessing as mp

# Forbidden Chars that cannot be used in file naming
FORBIDDEN_CHARS = ['<', '>', '*', '|', '?', '"', '/', ':', '\\']

# Camera Framerate
CAMERA_FRAMERATE = 30
PYCAP_FRAMERATE = getattr(FRAMERATE, 'FR_{}'.format(CAMERA_FRAMERATE))
# Camera Properties
CAMERA = 'camera'
VID_DIM = (480, 640)  # Rows, Cols
VID_DIM_RGB = (480, 640, 3)  # Rows, Cols, RGB
# CV2 Output Dimensions
MAP_DOWNSCALE = 2
MAP_DIMS = VID_DIM_RGB[0] // MAP_DOWNSCALE, VID_DIM_RGB[1] // MAP_DOWNSCALE, VID_DIM_RGB[2]
GRADIENT_HEIGHT = 100
PROGBAR_HEIGHT = GRADIENT_HEIGHT - 2

# Tracking Parameters
DEFAULT_BOUNDS = [(0, 0), (VID_DIM[1], VID_DIM[0])]
TOPLEFT = 'topleft'
TOPRIGHT = 'topright'
BOTTOMLEFT = 'bottomleft'
BOTTOMRIGHT = 'bottomright'

# Concurrency
MASTER_DUMP_QUEUE = mp.Queue()
PROC_HANDLER_QUEUE = mp.Queue()
EXP_START_EVENT = mp.Event()
# Process Names
PROC_CMR = 'proc_cmr'
PROC_CV2 = 'proc_cv2'
PROC_COORDS = 'proc_coords'
PROC_CMR_VIDREC = 'proc_cmr_vidrec'
PROC_CV2_VIDREC = 'proc_cv2_vidrec'
PROC_GUI = 'proc_gui'
# Queue Commands
CMD_START = 'cmd_start'
CMD_STOP = 'cmd_stop'
CMD_EXIT = 'cmd_exit'
CMD_SET_TIME = 'cmd_set_time'
CMD_SET_DIRS = 'cmd_set_dirs'
# Process Specific Commands
CMD_SET_VIDSRC = 'cmd_set_vidsrc'
CMD_SET_CMR_CONFIGS = 'cmd_set_cmr_configs'
CMD_GET_BG = 'cmd_get_bg'
CMD_CLR_MAPS = 'cmd_clr_maps'
CMD_SET_BOUNDS = 'cmd_set_bounds'
CMD_SHOW_TRACKED = 'cmd_show_tracked'
CMD_TARG_DRAW = 'cmd_targ_draw'
CMD_TARG_RADIUS = 'cmd_targ_radius'
CMD_NEW_BACKGROUND = 'cmd_new_background'
# Queue Messages
MSG_RECEIVED = 'msg_received'
MSG_STARTED = 'msg_started'
MSG_FINISHED = 'msg_finished'
MSG_VIDREC_SAVING = 'msg_vidrec_saving'
MSG_VIDREC_FINISHED = 'msg_vidrec_finished'
MSG_ERROR = 'msg_error'

# Directories and Saving
HOME_DIR = os.path.expanduser('~')

# Var names for Misc.CustomFunctions
DAY = 'day'
TIME = 'time'
HOUR = 'Hour'
MINS = 'Mins'
SECS = 'Secs'

# PyQt4
# Colors
qBlack = qg.QColor(0, 0, 0)
qWhite = qg.QColor(255, 255, 255)
qYellow = qg.QColor(255, 255, 0)
qBlue = qg.QColor(0, 0, 255)
qRed = qg.QColor(255, 0, 0)
qClear = qg.QColor(255, 255, 255, 0)
qSemi = qg.QColor(255, 255, 255, 128)
# Background Colors
qBgRed = 'background-color: rgb(255, 0, 0)'
qBgWhite = 'background-color: rgb(255, 255, 255)'
qBgCyan = 'background-color: cyan'
qBgOrange = 'background-color: orange'
# Selectable
qSelectable = qg.QGraphicsItem.ItemIsSelectable
# Layout
qAlignCenter = qc.Qt.AlignCenter
qStyleSunken = qg.QFrame.Sunken
qStylePanel = qg.QFrame.StyledPanel
# Keypresses
qKey_k = qc.Qt.Key_K
qKey_del = qc.Qt.Key_Delete
qKey_backspace = qc.Qt.Key_Backspace
# Key Modifiers
qMod_shift = qc.Qt.ShiftModifier
qMod_cntrl = qc.Qt.ControlModifier
qMod_alt = qc.Qt.AltModifier
# Signal Names
QT_GET_BOUNDS = 'qt_get_bounds'
QT_GOT_BOUNDS = 'qt_got_bounds'
