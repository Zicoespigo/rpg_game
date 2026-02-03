import pygame
from core.settings import *

class Camera:
    """
    Camera que segue o jogador com movimento suave (lerp).
    """
    def __init__(self):
        self.offset = pygame.Vector2(0, 0)
        self.smoothness = 0.1  # Quanto menor, mais suave (0.1 = 10% por frame)

    def update(self, target_rect):
        """
        Atualiza a posição da câmera para seguir o alvo.
        
        Args:
            target_rect: pygame.Rect do objeto a seguir (normalmente o jogador)
        """
        # Calcula a posição ideal (centrar o alvo no ecrã)
        target_x = target_rect.centerx - SCREEN_W // 2
        target_y = target_rect.centery - SCREEN_H // 2

        # Movimento suave (linear interpolation)
        self.offset.x += (target_x - self.offset.x) * self.smoothness
        self.offset.y += (target_y - self.offset.y) * self.smoothness

        # Limita a câmera aos limites do mapa
        self.offset.x = max(0, min(self.offset.x, MAP_W * TILE - SCREEN_W))
        self.offset.y = max(0, min(self.offset.y, MAP_H * TILE - SCREEN_H))

    def apply(self, rect):
        """
        Aplica o offset da câmera a um rect.
        
        Args:
            rect: pygame.Rect a transformar
            
        Returns:
            pygame.Rect com posição ajustada pela câmera
        """
        return rect.move(-self.offset.x, -self.offset.y)
