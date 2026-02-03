import pygame
import os
import random
from core.settings import *

class MenuManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MAIN_MENU"
        self.menu_bg = self.generate_dark_fantasy_bg()
        
        # Skill Tree State
        self.selected_skill = None
        self.show_confirm = False
        self.skill_rects = {}
        
        # Audio System - DESATIVADO
        self.current_music = ""
        self.click_sound = None
        self.fade_in_sound = None
        self.fade_out_sound = None
        
        # Menu Assets
        self.load_menu_assets()

    def log(self, msg):
        try:
            with open("erro_log.txt", "a") as f:
                f.write(msg + "\n")
            print(msg)
        except: pass

    def load_menu_assets(self):
        ROOT = os.path.abspath(os.getcwd())
        path = os.path.join(ROOT, 'assets/ui/menu/')
        self.assets = {}
        files = {
            'panel': 'panel_bg.png',
            'start_n': 'btn_start_normal.png',
            'start_h': 'btn_start_hover.png',
            'quit_n': 'btn_quit_normal.png',
            'quit_h': 'btn_quit_hover.png',
            'resume_n': 'btn_resume_normal.png',
            'resume_h': 'btn_resume_hover.png'
        }
        for key, filename in files.items():
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                try:
                    self.assets[key] = pygame.image.load(full_path).convert_alpha()
                except: pass

    def play_music(self, name):
        pass # Desativado

    def play_menu_music(self): pass
    def play_game_music(self): pass
    def play_skill_music(self): pass

    def generate_dark_fantasy_bg(self):
        bg = pygame.Surface((SCREEN_W, SCREEN_H))
        bg.fill((5, 5, 10))
        for _ in range(200):
            pygame.draw.circle(bg, (200, 210, 255), (random.randint(0, SCREEN_W), random.randint(0, SCREEN_H)), random.randint(1, 2))
        pygame.draw.polygon(bg, (15, 15, 25), [(0, SCREEN_H), (400, 300), (800, SCREEN_H)])
        pygame.draw.polygon(bg, (10, 10, 20), [(300, SCREEN_H), (800, 250), (1300, SCREEN_H)])
        return bg

    def handle_event(self, event, player=None):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == "PLAYING": self.state = "PAUSED"
                elif self.state == "PAUSED": self.state = "PLAYING"
            
            if event.key == pygame.K_c and player and not player.dead:
                if self.state == "PLAYING": self.state = "SKILL_TREE"
                elif self.state == "SKILL_TREE":
                    self.state = "PLAYING"
                    self.show_confirm = False
	
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == "MAIN_MENU":
                s_rect = pygame.Rect(SCREEN_W//2-120, 300, 240, 70)
                if s_rect.collidepoint(mouse_pos): return "NEW_GAME"
                e_rect = pygame.Rect(SCREEN_W//2-120, 400, 240, 70)
                if e_rect.collidepoint(mouse_pos): return "EXIT"
            
            if self.state == "SKILL_TREE" and player:
                return self.handle_skill_tree_events(event, player)
        return None

    def handle_skill_tree_events(self, event, player):
        mouse_pos = pygame.mouse.get_pos()
        if self.show_confirm:
            if SCREEN_W//2 - 110 < mouse_pos[0] < SCREEN_W//2 - 10 and SCREEN_H//2 + 50 < mouse_pos[1] < SCREEN_H//2 + 90:
                self.apply_skill(player)
                self.show_confirm = False
            if SCREEN_W//2 + 10 < mouse_pos[0] < SCREEN_W//2 + 110 and SCREEN_H//2 + 50 < mouse_pos[1] < SCREEN_H//2 + 90:
                self.show_confirm = False
            return None

        for skill, rect in self.skill_rects.items():
            if rect.collidepoint(mouse_pos) and player.skill_points > 0:
                self.selected_skill = skill
                self.show_confirm = True
        return None

    def apply_skill(self, player):
        if player.skill_points <= 0: return
        if self.selected_skill == "Strength": player.strength += 1
        elif self.selected_skill == "Agility": player.agility += 1
        elif self.selected_skill == "Vitality": player.vitality += 1
        player.skill_points -= 1
        player.update_stats()

    def draw(self, player=None):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == "MAIN_MENU":
            self.screen.blit(self.menu_bg, (0, 0))
            self.draw_text("MANUS RPG", 96, SCREEN_W//2, 150, (255, 215, 0))
            self.draw_text("THE DARK DESCENT", 32, SCREEN_W//2, 200, (150, 150, 150))
            s_rect = pygame.Rect(SCREEN_W//2-120, 300, 240, 70)
            color = (255, 255, 255) if s_rect.collidepoint(mouse_pos) else (200, 200, 200)
            pygame.draw.rect(self.screen, (30, 30, 45), s_rect, border_radius=15)
            pygame.draw.rect(self.screen, (180, 160, 120), s_rect, 2, border_radius=15)
            self.draw_text("NEW GAME", 48, s_rect.centerx, s_rect.centery, color)
            e_rect = pygame.Rect(SCREEN_W//2-120, 400, 240, 70)
            color = (255, 255, 255) if e_rect.collidepoint(mouse_pos) else (200, 200, 200)
            pygame.draw.rect(self.screen, (45, 30, 30), e_rect, border_radius=15)
            pygame.draw.rect(self.screen, (180, 160, 120), e_rect, 2, border_radius=15)
            self.draw_text("EXIT", 48, e_rect.centerx, e_rect.centery, color)
        elif self.state == "PAUSED":
            self.draw_overlay()
            p_rect = pygame.Rect(SCREEN_W//2-200, SCREEN_H//2-150, 400, 300)
            pygame.draw.rect(self.screen, (20, 20, 30), p_rect, border_radius=20)
            pygame.draw.rect(self.screen, (180, 160, 120), p_rect, 3, border_radius=20)
            self.draw_text("PAUSED", 64, SCREEN_W//2, p_rect.top + 60, (255, 215, 0))
            self.draw_text("PRESS ESC TO RESUME", 32, SCREEN_W//2, p_rect.bottom - 60, (150, 150, 150))
        elif self.state == "SKILL_TREE" and player:
            self.draw_skill_tree(player)

    def draw_overlay(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

    def draw_text(self, text, size, x, y, color=(255, 255, 255), center=True):
        try:
            font = pygame.font.SysFont("Arial", size, bold=True)
            surf = font.render(text, True, color)
            rect = surf.get_rect()
            if center: rect.center = (x, y)
            else: rect.topleft = (x, y)
            self.screen.blit(surf, rect)
        except: pass

    def draw_skill_tree(self, player):
        self.draw_overlay()
        panel_rect = pygame.Rect(0, 0, 600, 500)
        panel_rect.center = (SCREEN_W//2, SCREEN_H//2)
        pygame.draw.rect(self.screen, (30, 30, 45), panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, (180, 160, 120), panel_rect, 3, border_radius=15)
        self.draw_text("SKILL TREE", 54, SCREEN_W//2, panel_rect.top + 40, (255, 215, 0))
        self.draw_text(f"Available Points: {player.skill_points}", 32, SCREEN_W//2, panel_rect.top + 80)
        skills = [("Strength", player.strength, "+2 Damage"), ("Agility", player.agility, "+5 Stamina"), ("Vitality", player.vitality, "+10 Max HP")]
        mouse_pos = pygame.mouse.get_pos()
        self.skill_rects = {}
        for i, (name, val, desc) in enumerate(skills):
            y_pos = panel_rect.top + 150 + (i * 90)
            rect = pygame.Rect(panel_rect.left + 50, y_pos, 500, 70)
            self.skill_rects[name] = rect
            is_hover = rect.collidepoint(mouse_pos)
            pygame.draw.rect(self.screen, (50, 50, 70) if not is_hover else (70, 70, 100), rect, border_radius=10)
            pygame.draw.rect(self.screen, (180, 160, 120), rect, 1, border_radius=10)
            self.draw_text(f"{name}: {val}", 36, rect.left + 20, rect.centery, (255, 255, 255), False)
        if self.show_confirm: self.draw_confirmation()

    def draw_confirmation(self):
        conf_rect = pygame.Rect(0, 0, 400, 160)
        conf_rect.center = (SCREEN_W//2, SCREEN_H//2)
        pygame.draw.rect(self.screen, (20, 20, 30), conf_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 215, 0), conf_rect, 2, border_radius=10)
        self.draw_text(f"Upgrade {self.selected_skill}?", 32, SCREEN_W//2, conf_rect.top + 40)
        y_btn = pygame.Rect(SCREEN_W//2 - 110, SCREEN_H//2 + 20, 100, 40)
        pygame.draw.rect(self.screen, (40, 80, 40), y_btn, border_radius=5)
        self.draw_text("YES", 28, y_btn.centerx, y_btn.centery)
        n_btn = pygame.Rect(SCREEN_W//2 + 10, SCREEN_H//2 + 20, 100, 40)
        pygame.draw.rect(self.screen, (80, 40, 40), n_btn, border_radius=5)
        self.draw_text("NO", 28, n_btn.centerx, n_btn.centery)
