import pygame
import math
import array
import random


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.initialized = False

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.initialized = True
            self._generate_sounds()
        except Exception as e:
            print(f"音效系统初始化失败: {e}")
            self.initialized = False
            self.enabled = False

    def _generate_tone(self, frequency, duration, volume=0.3, wave_type='sine'):
        if not self.initialized:
            return None

        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            samples = array.array('h')

            for i in range(n_samples):
                t = i / sample_rate
                if wave_type == 'sine':
                    sample = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
                elif wave_type == 'square':
                    sample = int(32767 * volume * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1))
                elif wave_type == 'sawtooth':
                    sample = int(32767 * volume * (2 * (frequency * t - math.floor(0.5 + frequency * t))))
                elif wave_type == 'noise':
                    sample = int(32767 * volume * random.uniform(-1, 1))
                else:
                    sample = int(32767 * volume * math.sin(2 * math.pi * frequency * t))

                fade_factor = 1.0
                if i < n_samples * 0.1:
                    fade_factor = i / (n_samples * 0.1)
                elif i > n_samples * 0.7:
                    fade_factor = 1.0 - (i - n_samples * 0.7) / (n_samples * 0.3)
                sample = int(sample * fade_factor)

                samples.append(sample)
                samples.append(sample)

            return pygame.mixer.Sound(buffer=samples)
        except Exception as e:
            print(f"生成音效失败: {e}")
            return None

    def _generate_sounds(self):
        if not self.initialized:
            return

        self.sounds['slice'] = self._generate_slice_sound()
        self.sounds['explosion'] = self._generate_explosion_sound()
        self.sounds['golden'] = self._generate_golden_sound()
        self.sounds['combo'] = self._generate_combo_sound()
        self.sounds['fever'] = self._generate_fever_sound()

    def _generate_slice_sound(self):
        combined = []
        for freq in [800, 1200, 600]:
            sound = self._generate_tone(freq, 0.1, 0.2, 'sawtooth')
            if sound:
                combined.append(sound)
        return combined

    def _generate_explosion_sound(self):
        combined = []
        noise = self._generate_tone(100, 0.5, 0.4, 'noise')
        low = self._generate_tone(80, 0.4, 0.3, 'sine')
        if noise:
            combined.append(noise)
        if low:
            combined.append(low)
        return combined

    def _generate_golden_sound(self):
        combined = []
        for freq in [523, 659, 784, 1047]:
            sound = self._generate_tone(freq, 0.15, 0.25, 'sine')
            if sound:
                combined.append(sound)
        return combined

    def _generate_combo_sound(self):
        combined = []
        for freq in [440, 554, 659]:
            sound = self._generate_tone(freq, 0.1, 0.2, 'sine')
            if sound:
                combined.append(sound)
        return combined

    def _generate_fever_sound(self):
        combined = []
        for freq in [392, 494, 587, 784]:
            sound = self._generate_tone(freq, 0.2, 0.3, 'sine')
            if sound:
                combined.append(sound)
        return combined

    def _safe_play(self, sound_list):
        if not self.enabled or not self.initialized:
            return

        try:
            for sound in sound_list:
                if sound:
                    try:
                        channel = pygame.mixer.find_channel(True)
                        if channel:
                            channel.play(sound)
                    except:
                        try:
                            sound.play()
                        except:
                            pass
        except Exception as e:
            print(f"播放音效失败: {e}")

    def play_slice(self):
        if 'slice' in self.sounds:
            self._safe_play(self.sounds['slice'])

    def play_explosion(self):
        if 'explosion' in self.sounds:
            self._safe_play(self.sounds['explosion'])

    def play_golden(self):
        if 'golden' in self.sounds:
            self._safe_play(self.sounds['golden'])

    def play_combo(self):
        if 'combo' in self.sounds:
            self._safe_play(self.sounds['combo'])

    def play_fever(self):
        if 'fever' in self.sounds:
            self._safe_play(self.sounds['fever'])

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
