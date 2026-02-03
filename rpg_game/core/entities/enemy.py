import pygame
import os
import math
from core.settings import *
from core.animation.spritesheet import SpriteSheet
from core.ai.slime_ai import SlimeAI

FRAME = 64
IDLE_SPEED   = 0.10
HURT_SPEED   = 0.15
DEATH_SPEED  = 0.12
ATTACK_SPEED = 0.15

class SimpleSlime(pygame.sprite.Sprite):
    def __init__(self, pos, player):
        super().__init__()
        self.last_dir = "down"
        self.animations = self.load_animations()
        self.state = "idle_down"
        self.frame = 0.0
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        
        # --- Spawn e Tethering ---
        self.spawn_pos = pygame.Vector2(pos)
        self.tether_range = 400 # Distância máxima do spawn antes de voltar
        
        self.hp = 50
        self.max_hp = 50
        self.hurt = False
        self.dead = False
        self.attacking = False
        self.death_timer = 0
        self.fade_alpha = 255
        self.can_remove = False
        self.player = player
        self.game = None
        self.ai = SlimeAI(self, player)
        self.ai.attack_range = 22
        
        self.attack_timer = 0
        self.damage_applied = False
        self._load_sounds()

    def _load_sounds(self):
        ROOT = os.path.abspath(os.getcwd())
        # Slime Jump
        p_jump = os.path.join(ROOT, "assets/audio/slimejump.mp3")
        if not os.path.exists(p_jump): p_jump = os.path.join(ROOT, "assets/audio/slimejump")
        self.jump_sound = None
        if os.path.exists(p_jump):
            try:
                self.jump_sound = pygame.mixer.Sound(p_jump)
            except: pass
            
        # Slime Attack
        p_atk = os.path.join(ROOT, "assets/audio/slimeattack.mp3")
        if not os.path.exists(p_atk): p_atk = os.path.join(ROOT, "assets/audio/slimeattack")
        self.attack_sound = None
        if os.path.exists(p_atk):
            try:
                self.attack_sound = pygame.mixer.Sound(p_atk)
            except: pass

    def play_positional_sound(self, sound, max_vol=0.4):
        """Toca som com volume baseado na distância ao jogador."""
        if not sound or not self.player: return
        
        dist = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
        # Raio de audição: 600 pixels
        if dist > 600: return
        
        # Volume linear inverso: 1.0 na cara, 0.0 a 600px
        volume = max(0, max_vol * (1 - (dist / 600)))
        sound.set_volume(volume)
        sound.play()

    def load_sheet(self, path, frames, row=0):
        try:
            sheet = SpriteSheet(path, FRAME, FRAME)
            return sheet.get_row(row, frames)
        except:
            return [pygame.Surface((FRAME, FRAME)) for _ in range(frames)]

    def load_animations(self):
        ROOT = os.path.abspath(os.getcwd())
        p = lambda x: os.path.join(ROOT, x)
        
        states = {
            "idle": (p("assets/sprites/enemies/simple_slime/idle/spritesheet.png.png"), 6),
            "walk": (p("assets/sprites/enemies/simple_slime/walk/spritesheet.png.png"), 6),
            "attack": (p("assets/sprites/enemies/simple_slime/attack/spritesheet.png.png"), 8),
            "hurt": (p("assets/sprites/enemies/simple_slime/hurt/spritesheet.png.png"), 5)
        }
        
        a = {}
        for name, (path, frames) in states.items():
            a[f"{name}_right"] = self.load_sheet(path, frames, 0)
            a[f"{name}_up"]    = self.load_sheet(path, frames, 1)
            a[f"{name}_left"]  = self.load_sheet(path, frames, 2)
            a[f"{name}_down"]  = self.load_sheet(path, frames, 3)
            
        # Death costuma ser uma linha só ou repetida
        death_p = p("assets/sprites/enemies/simple_slime/death/spritesheet.png.png")
        a["death"] = self.load_sheet(death_p, 10, 0)
        
        return a

    def take_damage(self, dmg):
        if self.dead: return
        self.hp -= dmg
        self.hp = max(0, self.hp)
        if self.hp <= 0:
            self.dead = True
            self.attacking = False
            self.hurt = False
            self.frame = 0.0
            self.state = "death"
        else:
            self.hurt = True
            self.attacking = False
            self.frame = 0.0
            self.state = "hurt_" + self.last_dir

    def update_direction(self, move_vec):
        if move_vec.length_squared() > 0:
            if abs(move_vec.x) > abs(move_vec.y):
                self.last_dir = "right" if move_vec.x > 0 else "left"
            else:
                self.last_dir = "down" if move_vec.y > 0 else "up"

    def update(self):
        if self.can_remove: return
        if self.dead:
            self.state = "death"
            frames = self.animations["death"]
            if self.frame < len(frames) - 1:
                self.frame += DEATH_SPEED
            else:
                self.frame = len(frames) - 1
                self.death_timer += 1
                if self.death_timer > 180:
                    self.fade_alpha -= 5
                    if self.fade_alpha <= 0:
                        self.fade_alpha = 0
                        self.can_remove = True
            self.image = frames[int(self.frame)].copy()
            self.image.set_alpha(self.fade_alpha)
            return

        if self.attack_timer > 0: self.attack_timer -= 1

        if self.hurt:
            self.state = "hurt_" + self.last_dir
            self.frame += HURT_SPEED
            frames = self.animations.get(self.state, self.animations["hurt_down"])
            if self.frame >= len(frames):
                self.hurt = False
                self.frame = 0
                self.state = "idle_" + self.last_dir
            else:
                self.image = frames[int(self.frame)]
                return

        if self.attacking:
            self.state = "attack_" + self.last_dir
            self.frame += ATTACK_SPEED
            frames = self.animations.get(self.state, self.animations["attack_down"])
            
            # Som de ataque no início
            if int(self.frame) == 1 and not self.damage_applied:
                self.play_positional_sound(self.attack_sound, 0.5)

            if int(self.frame) == 4 and not self.damage_applied:
                self.damage_applied = True
                if self.player and not self.player.dead:
                    dist = pygame.Vector2(self.rect.center).distance_to(self.player.rect.center)
                    if dist < 32: self.player.take_damage(12)

            if self.frame >= len(frames):
                self.attacking = False
                self.damage_applied = False
                self.frame = 0
                self.state = "idle_" + self.last_dir
                self.attack_timer = 70
            else:
                self.image = frames[int(self.frame)]
                return

        # Lógica de Tethering e IA
        dist_to_spawn = pygame.Vector2(self.rect.center).distance_to(self.spawn_pos)
        
        if dist_to_spawn > self.tether_range:
            # Volta para o spawn
            dir_to_spawn = (self.spawn_pos - pygame.Vector2(self.rect.center)).normalize()
            self.update_direction(dir_to_spawn)
            self.rect.center += dir_to_spawn * ENEMY_SPEED
            self.state = "walk_" + self.last_dir
        else:
            ai_action = self.ai.update()
            if ai_action == "attack" and self.attack_timer == 0:
                self.attacking = True
                self.damage_applied = False
                self.frame = 0
                self.state = "attack_" + self.last_dir
            elif ai_action == "moving":
                # O movimento já é feito dentro do SlimeAI.update() no teu código original
                # mas precisamos garantir que a direção está correta
                # No teu SlimeAI.update(), ele move o rect diretamente.
                self.state = "walk_" + self.last_dir
            else:
                self.state = "idle_" + self.last_dir

        # Animação Idle/Walk e Som de Salto
        old_frame = int(self.frame)
        self.frame += IDLE_SPEED
        new_frame = int(self.frame)
        if old_frame != new_frame and new_frame == 3:
            self.play_positional_sound(self.jump_sound, 0.25)
            
        frames = self.animations.get(self.state, self.animations["idle_down"])
        if self.frame >= len(frames): self.frame = 0
        self.image = frames[int(self.frame)]

    def draw(self, screen, camera):
        if self.can_remove: return
        screen.blit(self.image, camera.apply(self.rect))
        if not self.dead:
            self.draw_health_bar(screen, camera)
    
    def draw_health_bar(self, screen, camera):
        bar_width = 40
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 8
        bar_rect = camera.apply(pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (80, 0, 0), bar_rect)
        health_width = int(bar_width * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (220, 0, 0), pygame.Rect(bar_rect.x, bar_rect.y, health_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), bar_rect, 1)
