import pygame
import os
import math
from core.settings import *
from core.animation.spritesheet import SpriteSheet

FRAME = 64
IDLE_SPEED   = 0.08
WALK_SPEED   = 0.08
RUN_SPEED    = 0.12
ATTACK_SPEED = 0.20

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.animations = self.load_animations()
        self.state = "idle_down"
        self.frame = 0.0
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2()
        self.last_dir = "down"
        self.look_vector = pygame.Vector2(0, 1)
        self.attacking = False
        self.attack_timer = 0
        self.attack_damage_done = False
        self.hurt = False
        self.hurt_timer = 0
        self.dead = False
        self.death_finished = False
        self.death_sound_played = False

        # --- Atributos Base ---
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.skill_points = 0
        
        self.strength = 5    # Aumenta Dano
        self.agility = 5     # Aumenta Velocidade e Stamina Max
        self.vitality = 5    # Aumenta HP Max
        
        self.max_hp = 100 + (self.vitality * 10)
        self.hp = self.max_hp
        self.max_stamina = 100 + (self.agility * 5)
        self.stamina = self.max_stamina
        self.stamina_recovery = 0.25 + (self.agility * 0.02)
        self.stamina_run_cost = 0.6
        self.can_run = True
        self.defense = 5
        
        self.game = None
        self._load_sounds()

    def _load_sounds(self):
        ROOT = os.path.abspath(os.getcwd())
        # Slash Sound
        s_path = os.path.join(ROOT, "assets/audio/slash.mp3")
        if not os.path.exists(s_path): s_path = os.path.join(ROOT, "assets/audio/slash")
        self.attack_sound = None
        if os.path.exists(s_path):
            try:
                self.attack_sound = pygame.mixer.Sound(s_path)
                self.attack_sound.set_volume(0.5)
            except: pass
            
        # Death Sound
        d_path = os.path.join(ROOT, "assets/audio/death.mp3")
        if not os.path.exists(d_path): d_path = os.path.join(ROOT, "assets/audio/death")
        self.death_sound = None
        if os.path.exists(d_path):
            try:
                self.death_sound = pygame.mixer.Sound(d_path)
                self.death_sound.set_volume(0.7)
            except: pass

    def load_sheet(self, path, frames, row):
        try:
            sheet = SpriteSheet(path, FRAME, FRAME)
            return sheet.get_row(row, frames)
        except:
            return [pygame.Surface((FRAME, FRAME)) for _ in range(frames)]

    def load_animations(self):
        ROOT = os.path.abspath(os.getcwd())
        p = lambda x: os.path.join(ROOT, x)
        a = {}
        idle_p = p("assets/sprites/player/idle/spritesheet.png.png")
        walk_p = p("assets/sprites/player/walk/spritesheet.png.png")
        run_p = p("assets/sprites/player/run/spritesheet.png.png")
        attack_p = p("assets/sprites/player/attack/spritesheet.png.png")
        hurt_p = p("assets/sprites/player/hurt/spritesheet.png.png")
        death_p = p("assets/sprites/player/death/spritesheet.png.png")

        a["idle_down"]  = self.load_sheet(idle_p, 5, 0)
        a["idle_left"]  = self.load_sheet(idle_p, 5, 1)
        a["idle_right"] = self.load_sheet(idle_p, 5, 2)
        a["idle_up"]    = self.load_sheet(idle_p, 5, 3)
        a["walk_down"]  = self.load_sheet(walk_p, 6, 0)
        a["walk_left"]  = self.load_sheet(walk_p, 6, 1)
        a["walk_right"] = self.load_sheet(walk_p, 6, 2)
        a["walk_up"]    = self.load_sheet(walk_p, 6, 3)
        a["run_down"]   = self.load_sheet(run_p, 8, 0)
        a["run_left"]   = self.load_sheet(run_p, 8, 1)
        a["run_right"]  = self.load_sheet(run_p, 8, 2)
        a["run_up"]     = self.load_sheet(run_p, 8, 3)
        a["attack_down"] = self.load_sheet(attack_p, 8, 0)
        a["attack_left"] = self.load_sheet(attack_p, 8, 1)
        a["attack_right"] = self.load_sheet(attack_p, 8, 2)
        a["attack_up"]   = self.load_sheet(attack_p, 8, 3)
        a["hurt_down"]   = self.load_sheet(hurt_p, 4, 0)
        a["hurt_left"]   = self.load_sheet(hurt_p, 4, 1)
        a["hurt_right"]  = self.load_sheet(hurt_p, 4, 2)
        a["hurt_up"]     = self.load_sheet(hurt_p, 4, 3)
        a["death_down"]  = self.load_sheet(death_p, 6, 0)
        a["death_left"]  = self.load_sheet(death_p, 6, 1)
        a["death_right"] = self.load_sheet(death_p, 6, 2)
        a["death_up"]    = self.load_sheet(death_p, 6, 3)
        return a

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.level_up()

    def level_up(self):
        self.xp -= self.xp_to_next
        self.level += 1
        self.skill_points += 1
        self.xp_to_next = int(self.xp_to_next * 1.2)
        self.hp = self.max_hp
        print(f"Level Up! Level: {self.level}")

    def update_stats(self):
        """Recalcula atributos baseados nos pontos de skill."""
        self.max_hp = 100 + (self.vitality * 10)
        self.max_stamina = 100 + (self.agility * 5)
        self.stamina_recovery = 0.25 + (self.agility * 0.02)
        self.defense = 5 + (self.strength // 2)

    def take_damage(self, dmg):
        if self.dead or self.hurt: return
        actual_damage = max(1, dmg - self.defense)
        self.hp -= actual_damage
        self.hp = max(0, self.hp)
        if self.hp <= 0:
            self.dead = True
            self.frame = 0.0
            self.state = "death_" + self.last_dir
            if self.death_sound and not self.death_sound_played:
                self.death_sound.play()
                self.death_sound_played = True
        else:
            self.hurt = True
            self.hurt_timer = 12
            self.frame = 0.0
            self.state = "hurt_" + self.last_dir

    def attack_enemies(self):
        if not self.game: return
        attack_range = TILE * 0.65
        cone_angle = 100
        damage = 15 + (self.strength * 2) # Dano escala com Força
        
        for enemy in self.game.enemies:
            if enemy.dead: continue
            enemy_vec = pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.rect.center)
            distance = enemy_vec.length()
            if distance < attack_range:
                if distance == 0: 
                    enemy.take_damage(damage)
                    continue
                enemy_vec = enemy_vec.normalize()
                dot = self.look_vector.dot(enemy_vec)
                dot = max(-1.0, min(1.0, dot))
                angle = math.degrees(math.acos(dot))
                if angle <= cone_angle / 2:
                    enemy.take_damage(damage)

    def update(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        if self.dead:
            self.frame += 0.1
            frames = self.animations[self.state]
            if self.frame >= len(frames):
                self.frame = len(frames) - 1
                self.death_finished = True
            self.image = frames[int(self.frame)]
            return

        if not (keys[pygame.K_LSHIFT] and self.direction.length_squared() > 0):
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_recovery)
        if self.stamina < 5: self.can_run = False
        if self.stamina > 30: self.can_run = True

        if self.hurt:
            self.hurt_timer -= 1
            self.frame += 0.2
            frames = self.animations[self.state]
            if self.frame >= len(frames): self.frame = len(frames) - 1
            self.image = frames[int(self.frame)]
            if self.hurt_timer <= 0:
                self.hurt = False
                self.state = "idle_" + self.last_dir
                self.frame = 0.0
            return

        if self.attacking:
            self.attack_timer -= 1
            self.frame += ATTACK_SPEED
            frames = self.animations[self.state]
            if int(self.frame) == 3 and not self.attack_damage_done:
                self.attack_damage_done = True
                self.attack_enemies()
            if self.frame >= len(frames):
                self.attacking = False
                self.attack_damage_done = False
                self.state = "idle_" + self.last_dir
                self.frame = 0.0
            else:
                self.image = frames[int(self.frame)]
            return

        # Velocidade escala com Agilidade
        RUN_SPEED_VAL = 3.5 + (self.agility * 0.1)
        WALK_SPEED_VAL = RUN_SPEED_VAL / 2
        
        self.direction.update(0, 0)
        old_dir = self.last_dir
        
        if keys[pygame.K_a]: self.direction.x = -1; self.last_dir = "left"; self.look_vector = pygame.Vector2(-1, 0)
        elif keys[pygame.K_d]: self.direction.x = 1; self.last_dir = "right"; self.look_vector = pygame.Vector2(1, 0)
        if keys[pygame.K_w]: self.direction.y = -1; self.last_dir = "up"; self.look_vector = pygame.Vector2(0, -1)
        elif keys[pygame.K_s]: self.direction.y = 1; self.last_dir = "down"; self.look_vector = pygame.Vector2(0, 1)

        if old_dir != self.last_dir: self.frame = 0.0

        if mouse[0]:
            self.attacking = True
            self.attack_timer = 14
            self.frame = 0.0
            self.state = "attack_" + self.last_dir
            if self.attack_sound: self.attack_sound.play()
            return

        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
            is_running = keys[pygame.K_LSHIFT] and self.can_run
            if is_running:
                self.stamina -= self.stamina_run_cost
                speed = RUN_SPEED_VAL
                self.state = "run_" + self.last_dir
            else:
                speed = WALK_SPEED_VAL
                self.state = "walk_" + self.last_dir
            old_pos = self.rect.center
            self.rect.center += self.direction * speed
            if self.game and not self.game.dungeon.is_position_valid(self.rect):
                self.rect.center = old_pos
        else:
            self.state = "idle_" + self.last_dir

        anim_speed = RUN_SPEED if "run" in self.state else WALK_SPEED if "walk" in self.state else IDLE_SPEED
        self.frame += anim_speed
        frames = self.animations[self.state]
        if self.frame >= len(frames): self.frame = 0.0
        self.image = frames[int(self.frame)]

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
