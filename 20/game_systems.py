import json
import os
import time
import pygame
from config import *


class Timer:
    def __init__(self):
        self.total_time = GAME_DURATION
        self.remaining_time = GAME_DURATION
        self.start_time = 0
        self.running = False
        self.paused = False
        self.pause_time = 0

    def start(self):
        self.start_time = time.time()
        self.remaining_time = self.total_time
        self.running = True
        self.paused = False

    def update(self):
        if not self.running or self.paused:
            return

        elapsed = time.time() - self.start_time
        self.remaining_time = max(0, self.total_time - elapsed)

        if self.remaining_time <= 0:
            self.running = False
            return False
        return True

    def add_time(self, seconds):
        self.total_time += seconds
        self.remaining_time += seconds

    def get_time_remaining(self):
        return int(self.remaining_time)

    def get_formatted_time(self):
        minutes = int(self.remaining_time) // 60
        seconds = int(self.remaining_time) % 60
        return f"{minutes}:{seconds:02d}"

    def is_time_up(self):
        return self.remaining_time <= 0

    def reset(self):
        self.total_time = GAME_DURATION
        self.remaining_time = GAME_DURATION
        self.start_time = 0
        self.running = False
        self.paused = False


class ComboSystem:
    def __init__(self):
        self.combo_count = 0
        self.last_slice_time = 0
        self.in_fever = False
        self.fever_start_time = 0
        self.score_multiplier = 1

    def on_fruit_sliced(self, current_time_ms):
        time_since_last_slice_ms = current_time_ms - self.last_slice_time
        time_since_last_slice_sec = time_since_last_slice_ms / 1000.0

        if time_since_last_slice_sec < COMBO_INTERVAL and self.last_slice_time > 0:
            self.combo_count += 1
        else:
            self.combo_count = 1

        self.last_slice_time = current_time_ms

        if self.combo_count >= COMBO_THRESHOLD and not self.in_fever:
            self._activate_fever(current_time_ms)
            return 'fever'

        if self.combo_count >= COMBO_THRESHOLD:
            return 'combo'

        return None

    def on_bomb_hit(self):
        self.combo_count = 0
        self.in_fever = False
        self.score_multiplier = 1

    def _activate_fever(self, current_time):
        self.in_fever = True
        self.fever_start_time = current_time
        self.score_multiplier = FEVER_MULTIPLIER

    def update(self, current_time):
        if self.in_fever:
            elapsed = (current_time - self.fever_start_time) / 1000.0
            if elapsed >= FEVER_DURATION:
                self.in_fever = False
                self.score_multiplier = 1
                self.combo_count = 0

        if self.combo_count > 0:
            time_since_last_slice = (current_time - self.last_slice_time) / 1000.0
            if time_since_last_slice > COMBO_INTERVAL and not self.in_fever:
                self.combo_count = 0

    def get_fever_remaining(self):
        if not self.in_fever:
            return 0
        current_time_ms = pygame.time.get_ticks()
        elapsed_sec = (current_time_ms - self.fever_start_time) / 1000.0
        return max(0, FEVER_DURATION - elapsed_sec)

    def reset(self):
        self.combo_count = 0
        self.last_slice_time = 0
        self.in_fever = False
        self.fever_start_time = 0
        self.score_multiplier = 1


class ScoreManager:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self._load_high_score()

    def add_score(self, base_score, multiplier=1):
        actual_score = base_score * multiplier
        self.score += actual_score
        return actual_score

    def subtract_score(self, penalty):
        self.score = max(0, self.score - penalty)

    def get_score(self):
        return self.score

    def get_high_score(self):
        return self.high_score

    def is_new_high_score(self):
        return self.score > self.high_score

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def _load_high_score(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
        except (json.JSONDecodeError, IOError):
            self.high_score = 0

    def _save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except IOError:
            pass

    def reset(self):
        self.score = 0
