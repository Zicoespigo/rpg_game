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
        
        # Carregar assets da UI
        self.ui_panel = None
        self._load_ui_assets()
        
        self.play_game_music()
    
    def _load_ui_assets(self):
        ROOT = os.path.abspath(os.getcwd())
        path = os.path.join(ROOT, "assets/ui/character_panel.png")
        if os.path.exists(path):
            try:
                full_sheet = pygame.image.load(path).convert_alpha()
                # Extrair o primeiro painel (com o rosto do personagem)
                # Baseado na imagem, o painel tem aproximadamente 100x40 pixels, vamos escalar para ficar visível
                self.ui_panel = full_sheet.subsurface((0, 0, 100, 42))
                self.ui_panel = pygame.transform.scale(self.ui_panel, (250, 105))
            except: pass

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
        ui_x, ui_y = 20, 20
        
        if self.ui_panel:
            self.screen.blit(self.ui_panel, (ui_x, ui_y))
            
            # Coordenadas relativas para as barras dentro do painel escalado (250x105)
            # HP BAR (Vermelha)
            hp_ratio = max(0, self.player.hp / self.player.max_hp)
            pygame.draw.rect(self.screen, (200, 50, 50), (ui_x + 85, ui_y + 25, int(145 * hp_ratio), 10))
            
            # STAMINA BAR (Azul)
            st_ratio = max(0, self.player.stamina / self.player.max_stamina)
            pygame.draw.rect(self.screen, (50, 150, 200), (ui_x + 85, ui_y + 46, int(145 * st_ratio), 10))
            
            # XP BAR (Roxa/Verde conforme a imagem)
            xp_ratio = min(1.0, self.player.xp / self.player.xp_to_next)
            pygame.draw.rect(self.screen, (100, 200, 50), (ui_x + 85, ui_y + 68, int(145 * xp_ratio), 8))
        else:
            # Fallback se a imagem falhar
            bar_w, bar_h = 240, 20
            pygame.draw.rect(self.screen, (40, 40, 40), (ui_x, ui_y, bar_w, bar_h))
            hp_ratio = max(0, self.player.hp / self.player.max_hp)
            if hp_ratio > 0:
                pygame.draw.rect(self.screen, (200, 50, 50), (ui_x, ui_y, int(bar_w * hp_ratio), bar_h))
            pygame.draw.rect(self.screen, (180, 160, 120), (ui_x, ui_y, bar_w, bar_h), 2)

        # Stats Text
        lvl_text = self.font_small.render(f"LVL {self.player.level}", True, (255, 255, 255))
        self.screen.blit(lvl_text, (ui_x + 10, ui_y + 110))
        
        if self.player.skill_points > 0:
            sp_text = self.font_small.render(f"PONTOS: {self.player.skill_points} (C)", True, (0, 255, 100))
            self.screen.blit(sp_text, (ui_x + 80, ui_y + 110))

        if self.player.dead:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            msg = self.font_main.render("VOCÊ MORREU", True, (200, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
