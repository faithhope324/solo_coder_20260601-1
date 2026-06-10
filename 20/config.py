SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (240, 245, 250)

GRAVITY = 0.4
SPAWN_Y = 500
MIN_VELOCITY_X = -3
MAX_VELOCITY_X = 3
MIN_VELOCITY_Y = -12
MAX_VELOCITY_Y = -8

FRUIT_TYPES = {
    'apple': {'color': (255, 80, 80), 'radius': 30, 'score': 10},
    'banana': {'color': (255, 230, 80), 'radius': 35, 'score': 15},
    'orange': {'color': (255, 165, 0), 'radius': 32, 'score': 20},
    'watermelon': {'color': (60, 180, 80), 'radius': 40, 'score': 30}
}

GOLDEN_BANANA = {
    'color': (255, 215, 0),
    'radius': 38,
    'score': 100,
    'time_bonus': 3,
    'interval': 10
}

BOMB = {
    'color': (30, 30, 30),
    'fuse_color': (255, 50, 50),
    'radius': 35,
    'penalty': 50
}

SLICE_COLOR = (255, 50, 50)
SLICE_ALPHA = 180
SLICE_LINE_WIDTH = 4
TRAIL_LENGTH = 10

GAME_DURATION = 60
COMBO_THRESHOLD = 3
COMBO_INTERVAL = 1.0
FEVER_DURATION = 5.0
FEVER_MULTIPLIER = 2

HIGHSCORE_FILE = 'highscore.json'

FPS = 60
