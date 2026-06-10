import math
import pygame
from config import *


class UIRenderer:
    def __init__(self):
        self.fonts = {}
        self._init_fonts()
        self.fever_glow_phase = 0

    def _init_fonts(self):
        chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong', 'Arial Unicode MS']
        font_small = None
        font_medium = None
        font_large = None
        font_xlarge = None

        for font_name in chinese_fonts:
            try:
                test_font = pygame.font.SysFont(font_name, 20)
                if test_font.size('测试')[0] > 0:
                    font_small = pygame.font.SysFont(font_name, 20, bold=True)
                    font_medium = pygame.font.SysFont(font_name, 28, bold=True)
                    font_large = pygame.font.SysFont(font_name, 48, bold=True)
                    font_xlarge = pygame.font.SysFont(font_name, 72, bold=True)
                    break
            except:
                continue

        if font_small is None:
            font_small = pygame.font.Font(None, 20)
            font_medium = pygame.font.Font(None, 28)
            font_large = pygame.font.Font(None, 48)
            font_xlarge = pygame.font.Font(None, 72)

        self.fonts['small'] = font_small
        self.fonts['medium'] = font_medium
        self.fonts['large'] = font_large
        self.fonts['xlarge'] = font_xlarge

    def draw_hud(self, surface, score, time_str, combo_count, in_fever, fever_remaining):
        self._draw_score(surface, score)
        self._draw_time(surface, time_str)

        if combo_count >= COMBO_THRESHOLD and not in_fever:
            self._draw_combo(surface, combo_count)

        if in_fever:
            self._draw_fever_effect(surface, fever_remaining)

    def _draw_score(self, surface, score):
        score_text = self.fonts['large'].render(f"分数: {score}", True, (50, 50, 50))
        score_rect = score_text.get_rect()
        score_rect.topright = (SCREEN_WIDTH - 20, 15)
        surface.blit(score_text, score_rect)

        shadow_text = self.fonts['large'].render(f"分数: {score}", True, (200, 200, 200))
        shadow_rect = shadow_text.get_rect()
        shadow_rect.topright = (SCREEN_WIDTH - 18, 17)
        surface.blit(shadow_text, shadow_rect)
        surface.blit(score_text, score_rect)

    def _draw_time(self, surface, time_str):
        time_color = (50, 50, 50)
        try:
            seconds = int(time_str.split(':')[1])
            minutes = int(time_str.split(':')[0])
            total_seconds = minutes * 60 + seconds
            if total_seconds <= 10:
                time_color = (255, 50, 50)
        except:
            pass

        time_text = self.fonts['medium'].render(f"时间: {time_str}", True, time_color)
        time_rect = time_text.get_rect()
        time_rect.topright = (SCREEN_WIDTH - 20, 70)
        surface.blit(time_text, time_rect)

    def _draw_combo(self, surface, combo_count):
        combo_text = self.fonts['large'].render(f"连击 x{combo_count}!", True, (255, 140, 0))
        combo_rect = combo_text.get_rect()
        combo_rect.center = (SCREEN_WIDTH // 2, 80)

        glow_surface = pygame.Surface((combo_rect.width + 20, combo_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 200, 100, 100), glow_surface.get_rect())
        glow_rect = glow_surface.get_rect(center=combo_rect.center)
        surface.blit(glow_surface, glow_rect)

        surface.blit(combo_text, combo_rect)

    def _draw_fever_effect(self, surface, fever_remaining):
        self.fever_glow_phase += 0.1
        glow_intensity = (math.sin(self.fever_glow_phase) + 1) / 2

        border_size = 30
        for i in range(5):
            alpha = int(100 * glow_intensity * (1 - i * 0.2))
            border_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, (255, 100 + int(100 * glow_intensity), 50, alpha),
                           (i * 5, i * 5, SCREEN_WIDTH - i * 10, SCREEN_HEIGHT - i * 10),
                           border_size - i * 5)
            surface.blit(border_surface, (0, 0))

        fever_text = self.fonts['xlarge'].render("狂热模式!", True, (255, 200, 50))
        fever_rect = fever_text.get_rect()
        fever_rect.center = (SCREEN_WIDTH // 2, 100)
        surface.blit(fever_text, fever_rect)

        fever_bar_width = 200
        fever_bar_height = 15
        fever_bar_x = SCREEN_WIDTH // 2 - fever_bar_width // 2
        fever_bar_y = 150

        pygame.draw.rect(surface, (80, 80, 80),
                        (fever_bar_x, fever_bar_y, fever_bar_width, fever_bar_height))

        fever_progress = fever_remaining / FEVER_DURATION
        pygame.draw.rect(surface, (255, 150, 50),
                        (fever_bar_x, fever_bar_y, int(fever_bar_width * fever_progress), fever_bar_height))

        mult_text = self.fonts['medium'].render(f"得分 x{FEVER_MULTIPLIER}", True, (255, 220, 100))
        mult_rect = mult_text.get_rect()
        mult_rect.center = (SCREEN_WIDTH // 2, 185)
        surface.blit(mult_text, mult_rect)

    def draw_start_screen(self, surface, high_score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((240, 245, 250, 230))
        surface.blit(overlay, (0, 0))

        title_text = self.fonts['xlarge'].render("水果忍者", True, (50, 150, 50))
        title_rect = title_text.get_rect()
        title_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        surface.blit(title_text, title_rect)

        subtitle_text = self.fonts['medium'].render("滑动鼠标切开水果！", True, (80, 80, 80))
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        surface.blit(subtitle_text, subtitle_rect)

        if high_score > 0:
            hs_text = self.fonts['medium'].render(f"最高分: {high_score}", True, (255, 150, 50))
            hs_rect = hs_text.get_rect()
            hs_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
            surface.blit(hs_text, hs_rect)

        start_text = self.fonts['large'].render("点击开始游戏", True, (100, 100, 100))
        start_rect = start_text.get_rect()
        start_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)

        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
        pulse_color = (int(100 + 50 * pulse), int(100 + 50 * pulse), int(100 + 50 * pulse))
        pulse_text = self.fonts['large'].render("点击开始游戏", True, pulse_color)
        surface.blit(pulse_text, start_rect)

        tip_text = self.fonts['small'].render("躲避炸弹！金色香蕉可增加时间！", True, (120, 120, 120))
        tip_rect = tip_text.get_rect()
        tip_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        surface.blit(tip_text, tip_rect)

    def draw_game_over(self, surface, score, high_score, is_new_high_score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        game_over_text = self.fonts['xlarge'].render("游戏结束", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect()
        game_over_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        surface.blit(game_over_text, game_over_rect)

        if is_new_high_score:
            new_hs_text = self.fonts['large'].render("新纪录！", True, (255, 215, 0))
            new_hs_rect = new_hs_text.get_rect()
            new_hs_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 20)
            surface.blit(new_hs_text, new_hs_rect)

        score_text = self.fonts['large'].render(f"最终得分: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect()
        score_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        surface.blit(score_text, score_rect)

        hs_text = self.fonts['medium'].render(f"最高分: {high_score}", True, (255, 200, 100))
        hs_rect = hs_text.get_rect()
        hs_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        surface.blit(hs_text, hs_rect)

        restart_text = self.fonts['large'].render("点击重新开始", True, (200, 200, 200))
        restart_rect = restart_text.get_rect()
        restart_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)

        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
        pulse_color = (int(200 + 55 * pulse), int(200 + 55 * pulse), int(200 + 55 * pulse))
        pulse_text = self.fonts['large'].render("点击重新开始", True, pulse_color)
        surface.blit(pulse_text, restart_rect)

    def draw_score_popup(self, surface, x, y, score, color=(255, 255, 100)):
        pass
