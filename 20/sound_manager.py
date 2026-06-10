import pygame
import math
import array


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.enabled = True
        self._generate_sounds()

    def _generate_sounds(self):
        self.sounds['slice'] = self._generate_slice_sound()
        self.sounds['explosion'] = self._generate_explosion_sound()
        self.sounds['golden'] = self._generate_golden_sound()
        self.sounds['combo'] = self._generate_combo_sound()
        self.sounds['fever'] = self._generate_fever_sound()

    def _generate_tone(self, frequency, duration, volume=0.3, wave_type='sine'):
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
                import random
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

    def _generate_slice_sound(self):
        combined = []
        for freq in [800, 1200, 600]:
            sound = self._generate_tone(freq, 0.1, 0.2, 'sawtooth')
            combined.append(sound)
        return combined

    def _generate_explosion_sound(self):
        combined = []
        noise = self._generate_tone(100, 0.5, 0.4, 'noise')
        low = self._generate_tone(80, 0.4, 0.3, 'sine')
        combined.append(noise)
        combined.append(low)
        return combined

    def _generate_golden_sound(self):
        combined = []
        for freq in [523, 659, 784, 1047]:
            sound = self._generate_tone(freq, 0.15, 0.25, 'sine')
            combined.append(sound)
        return combined

    def _generate_combo_sound(self):
        combined = []
        for freq in [440, 554, 659]:
            sound = self._generate_tone(freq, 0.1, 0.2, 'sine')
            combined.append(sound)
        return combined

    def _generate_fever_sound(self):
        combined = []
        for freq in [392, 494, 587, 784]:
            sound = self._generate_tone(freq, 0.2, 0.3, 'sine')
            combined.append(sound)
        return combined

    def play(self, sound_name):
        if not self.enabled:
            return

        if sound_name in self.sounds:
            sounds = self.sounds[sound_name]
            if isinstance(sounds, list):
                for i, sound in enumerate(sounds):
                    pygame.time.set_timer(pygame.USEREVENT + i, i * 50)
                    sound.play()
            else:
                sounds.play()

    def play_slice(self):
        if self.enabled and 'slice' in self.sounds:
            for i, sound in enumerate(self.sounds['slice']):
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound, maxtime=0, fade_ms=0)

    def play_explosion(self):
        if self.enabled and 'explosion' in self.sounds:
            for sound in self.sounds['explosion']:
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound)

    def play_golden(self):
        if self.enabled and 'golden' in self.sounds:
            for i, sound in enumerate(self.sounds['golden']):
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound)

    def play_combo(self):
        if self.enabled and 'combo' in self.sounds:
            for sound in self.sounds['combo']:
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound)

    def play_fever(self):
        if self.enabled and 'fever' in self.sounds:
            for sound in self.sounds['fever']:
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.play(sound)

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
