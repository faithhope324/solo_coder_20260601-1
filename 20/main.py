import pygame
import sys
import time
from config import *
from fruit_generator import FruitGenerator
from mouse_tracker import MouseTracker
from particle_system import ParticleSystem
from sound_manager import SoundManager
from game_systems import Timer, ComboSystem, ScoreManager
from ui_renderer import UIRenderer


class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    GAME_OVER = 'game_over'


class FruitNinjaGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Fruit Ninja - Simplified")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.state = GameState.MENU

        self.fruit_generator = FruitGenerator()
        self.mouse_tracker = MouseTracker()
        self.particle_system = ParticleSystem()
        self.sound_manager = SoundManager()
        self.timer = Timer()
        self.combo_system = ComboSystem()
        self.score_manager = ScoreManager()
        self.ui_renderer = UIRenderer()

        self.mouse_down = False
        self.mouse_pos = (0, 0)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_down = True
                    if self.state == GameState.MENU:
                        self.start_game()
                    elif self.state == GameState.GAME_OVER:
                        self.restart_game()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                    else:
                        self.quit_game()
                elif event.key == pygame.K_m:
                    self.sound_manager.toggle()

    def start_game(self):
        self.state = GameState.PLAYING
        self.fruit_generator.reset()
        self.mouse_tracker.reset()
        self.particle_system.reset()
        self.timer.start()
        self.combo_system.reset()
        self.score_manager.reset()

    def restart_game(self):
        self.start_game()

    def quit_game(self):
        self.score_manager.save_high_score()
        pygame.quit()
        sys.exit()

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state != GameState.PLAYING:
            return

        if not self.timer.update():
            self.end_game()
            return

        self.fruit_generator.update(current_time)
        self.mouse_tracker.update(self.mouse_pos, self.mouse_down)
        self.particle_system.update()
        self.combo_system.update(current_time)

        active_fruits = self.fruit_generator.get_active_fruits()
        sliced_fruits = self.mouse_tracker.check_collisions(active_fruits)

        for fruit in sliced_fruits:
            if fruit.is_bomb:
                self._handle_bomb_hit(fruit)
            else:
                self._handle_fruit_sliced(fruit, current_time)

    def _handle_fruit_sliced(self, fruit, current_time):
        self.particle_system.create_slice_particles(fruit)
        self.particle_system.create_fruit_halves(fruit)
        self.sound_manager.play_slice()

        combo_result = self.combo_system.on_fruit_sliced(current_time)

        if combo_result == 'fever':
            self.sound_manager.play_fever()
        elif combo_result == 'combo':
            self.sound_manager.play_combo()

        base_score = fruit.score
        multiplier = self.combo_system.score_multiplier

        if fruit.is_golden:
            self.sound_manager.play_golden()
            self.timer.add_time(GOLDEN_BANANA['time_bonus'])

        self.score_manager.add_score(base_score, multiplier)

    def _handle_bomb_hit(self, bomb):
        self.particle_system.create_explosion(bomb.x, bomb.y)
        self.sound_manager.play_explosion()
        self.score_manager.subtract_score(BOMB['penalty'])
        self.combo_system.on_bomb_hit()

    def end_game(self):
        self.state = GameState.GAME_OVER
        self.score_manager.save_high_score()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        if self.state == GameState.MENU:
            self.ui_renderer.draw_start_screen(self.screen, self.score_manager.get_high_score())
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.GAME_OVER:
            self._draw_game()
            self.ui_renderer.draw_game_over(
                self.screen,
                self.score_manager.get_score(),
                self.score_manager.get_high_score(),
                self.score_manager.is_new_high_score()
            )

        pygame.display.flip()

    def _draw_game(self):
        self.fruit_generator.draw(self.screen)
        self.particle_system.draw(self.screen)
        self.mouse_tracker.draw(self.screen)

        if self.state == GameState.PLAYING:
            self.ui_renderer.draw_hud(
                self.screen,
                self.score_manager.get_score(),
                self.timer.get_formatted_time(),
                self.combo_system.combo_count,
                self.combo_system.in_fever,
                self.combo_system.get_fever_remaining()
            )

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = FruitNinjaGame()
    game.run()
