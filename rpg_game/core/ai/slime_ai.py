import pygame
from core.ai.base_ai import BaseAI
from core.settings import *

class SlimeAI(BaseAI):
    """
    IA para o inimigo Slime: persegue o jogador e decide quando atacar.
    """
    def __init__(self, owner, player):
        super().__init__(owner)
        self.player = player
        self.attack_range = 45 # Ligeiramente maior para garantir colisão visual
        self.move_speed = ENEMY_SPEED
    
    def update(self):
        """
        Atualiza a lógica da IA e retorna a ação desejada.
        """
        if not self.player or self.owner.dead or self.owner.hurt:
            return "idle"
        
        # Calcula vetor para o jogador
        direction = pygame.Vector2(
            self.player.rect.centerx - self.owner.rect.centerx,
            self.player.rect.centery - self.owner.rect.centery
        )
        
        distance = direction.length()
        
        # Se estiver muito perto e o cooldown permitir, ataca
        if distance <= self.attack_range:
            if self.owner.attack_timer == 0:
                return "attack"
            else:
                return "idle"
        
        # Se estiver no alcance de visão, persegue
        elif distance < 350:
            if distance != 0:
                direction = direction.normalize()
            
            # Move o inimigo
            old_pos = self.owner.rect.center
            self.owner.rect.center += direction * self.move_speed
            
            # Verifica colisão com mapa
            if self.owner.game and not self.owner.game.dungeon.is_position_valid(self.owner.rect):
                self.owner.rect.center = old_pos
            
            return "moving"
            
        return "idle"
