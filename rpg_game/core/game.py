import pygame
import os
import random
from core.settings import *
from core.entities.player import Player
from core.entities.enemy import SimpleSlime
from core.map import Dungeon
from core.camera import Camera

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.dungeon = Dungeon()
        
        spawn_x = (MAP_W * TILE) // 2
        spawn_y = (MAP_H * TILE) // 2
        self.player = Player((spawn_x, spawn_y))
        self.player.game = self
        
        self.camera = Camera()
        self.enemies = []
        self._spawn_initial_horde(25) # Spawn inicial de 25 slimes
        
        self.font_small = pygame.font.Font(None, 24)
        self.font_main = pygame.font.Font(None, 54)
        
        self.play_game_music()
    
    def play_game_music(self):
        ROOT = os.path.abspath(os.getcwd())
        path = os.path.join(ROOT, "assets/audio/backgroundMP3.mp3")
        if os.path.exists(path):
            try:
                if not pygame.mixer.get_init(): pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.3)
            except: pass

    def _spawn_initial_horde(self, count):
        for _ in range(count):
            while True:
                rx = random.randint(TILE * 2, (MAP_W - 2) * TILE)
                ry = random.randint(TILE * 2, (MAP_H - 2) * TILE)
                # Evitar spawn em cima do jogador
                dist = ((rx - self.player.rect.centerx)**2 + (ry - self.player.rect.centery)**2)**0.5
                if dist > 500:
                    enemy = SimpleSlime((rx, ry), self.player)
                    enemy.game = self
                    self.enemies.append(enemy)
                    break
    
    def update(self):
        if self.player.dead: return
        
        self.player.update()
        for enemy in self.enemies[:]:
            enemy.update()
            
            # Se o inimigo morrer, dá XP e remove
            if enemy.dead and not hasattr(enemy, 'xp_given'):
                self.player.add_xp(40) # Aumentado XP por kill
                enemy.xp_given = True
            
            if enemy.can_remove:
                self.enemies.remove(enemy)
                # Respawn automático para manter a densidade
                self._spawn_initial_horde(1)
                
        self.camera.update(self.player.rect)
    
    def draw(self):
        self.dungeon.draw(self.screen, self.camera)
        
        # Y-sorting para profundidade
        all_entities = self.enemies + [self.player]
        all_entities.sort(key=lambda e: e.rect.bottom)
        
        for entity in all_entities:
            entity.draw(self.screen, self.camera)
            
        self.draw_interface()
    
    def draw_interface(self):
        ui_x, ui_y = 30, 30
        bar_w, bar_h = 240, 20
        
        # HP BAR
        pygame.draw.rect(self.screen, (40, 40, 40), (ui_x, ui_y, bar_w, bar_h))
        hp_ratio = max(0, self.player.hp / self.player.max_hp)
        if hp_ratio > 0:
            pygame.draw.rect(self.screen, (200, 50, 50), (ui_x, ui_y, int(bar_w * hp_ratio), bar_h))
        pygame.draw.rect(self.screen, (180, 160, 120), (ui_x, ui_y, bar_w, bar_h), 2)
        
        # STAMINA BAR
        st_y = ui_y + 30
        pygame.draw.rect(self.screen, (40, 40, 40), (ui_x, st_y, bar_w, bar_h))
        st_ratio = max(0, self.player.stamina / self.player.max_stamina)
        if st_ratio > 0:
            pygame.draw.rect(self.screen, (50, 150, 200), (ui_x, st_y, int(bar_w * st_ratio), bar_h))
        pygame.draw.rect(self.screen, (180, 160, 120), (ui_x, st_y, bar_w, bar_h), 2)

        # XP BAR (Agora mais visível)
        xp_y = st_y + 30
        pygame.draw.rect(self.screen, (40, 40, 40), (ui_x, xp_y, bar_w, 12))
        xp_ratio = min(1.0, self.player.xp / self.player.xp_to_next)
        if xp_ratio > 0:
            pygame.draw.rect(self.screen, (150, 50, 200), (ui_x, xp_y, int(bar_w * xp_ratio), 12))
        pygame.draw.rect(self.screen, (180, 160, 120), (ui_x, xp_y, bar_w, 12), 1)

        # Stats Text
        lvl_text = self.font_small.render(f"LEVEL {self.player.level}", True, (255, 255, 255))
        self.screen.blit(lvl_text, (ui_x, xp_y + 18))
        
        if self.player.skill_points > 0:
            sp_text = self.font_small.render(f"SKILL POINTS: {self.player.skill_points} (C)", True, (0, 255, 100))
            self.screen.blit(sp_text, (ui_x + 100, xp_y + 18))

        if self.player.dead:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            msg = self.font_main.render("VOCÊ MORREU", True, (200, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
