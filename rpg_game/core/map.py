import pygame
import random
from core.settings import *

class Dungeon:
    def __init__(self):
        self.width = MAP_W * TILE
        self.height = MAP_H * TILE
        self.floor_surf = pygame.Surface((self.width, self.height))
        self.generate_3d_fantasy_map()

    def generate_3d_fantasy_map(self):
        """Gera um mapa com relevo ilusório, neve e estética Dark Fantasy."""
        # Cores Dark Fantasy / Neve
        base_floor = (25, 25, 35)      # Chão escuro/azulado
        snow_color = (180, 190, 210)   # Neve acumulada
        elevation_color = (45, 45, 60) # Nível superior
        shadow_color = (10, 10, 15)    # Sombra profunda
        
        self.floor_surf.fill(base_floor)
        
        for y in range(MAP_H):
            for x in range(MAP_W):
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                
                # --- Lógica de Relevo Ilusório ---
                # Criamos "plataformas" usando lógica de coordenadas
                is_elevated = (x > 10 and x < 20 and y > 10 and y < 20) or \
                              (x > 30 and x < 45 and y > 25 and y < 40)
                
                if is_elevated:
                    pygame.draw.rect(self.floor_surf, elevation_color, rect)
                    # Borda de luz no topo para parecer que está acima
                    pygame.draw.line(self.floor_surf, (80, 80, 100), (rect.x, rect.y), (rect.right, rect.y), 2)
                else:
                    # Chão normal com textura de pedra
                    pygame.draw.rect(self.floor_surf, base_floor, rect)
                    pygame.draw.rect(self.floor_surf, (35, 35, 45), rect, 1) # Grelha subtil
                
                # --- Adicionar Neve ---
                # Neve cai aleatoriamente, mas acumula-se mais nas bordas (cantos)
                if random.random() < 0.15:
                    snow_size = random.randint(2, 6)
                    pygame.draw.circle(self.floor_surf, snow_color, 
                                     (rect.x + random.randint(0, TILE), rect.y + random.randint(0, TILE)), 
                                     snow_size)
                
                # --- Sombras de Relevo (O Truque Visual) ---
                # Se o tile à esquerda é elevado e este não é, desenha sombra à direita da plataforma
                if x > 0 and (x-1 > 10 and x-1 < 20 and y > 10 and y < 20) and not is_elevated:
                    pygame.draw.rect(self.floor_surf, shadow_color, (rect.x, rect.y, 8, TILE))
                
                # Sombra abaixo da plataforma
                if y > 0 and (x > 10 and x < 20 and y-1 > 10 and y-1 < 20) and not is_elevated:
                    pygame.draw.rect(self.floor_surf, shadow_color, (rect.x, rect.y, TILE, 8))

        # Bordas do Mapa (Muralhas de Gelo/Pedra)
        for i in range(MAP_W):
            # Topo e Fundo
            pygame.draw.rect(self.floor_surf, (10, 10, 20), (i*TILE, 0, TILE, TILE))
            pygame.draw.rect(self.floor_surf, (10, 10, 20), (i*TILE, (MAP_H-1)*TILE, TILE, TILE))
        for i in range(MAP_H):
            # Esquerda e Direita
            pygame.draw.rect(self.floor_surf, (10, 10, 20), (0, i*TILE, TILE, TILE))
            pygame.draw.rect(self.floor_surf, (10, 10, 20), ((MAP_W-1)*TILE, i*TILE, TILE, TILE))

    def is_position_valid(self, rect):
        if rect.left < TILE or rect.right > self.width - TILE: return False
        if rect.top < TILE or rect.bottom > self.height - TILE: return False
        return True

    def draw(self, screen, camera):
        screen.blit(self.floor_surf, camera.apply(pygame.Rect(0, 0, self.width, self.height)))
