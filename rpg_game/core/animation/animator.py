class Animator:
    """
    Gerencia animações de sprites com múltiplos estados.
    """
    def __init__(self, animations, initial_state):
        """
        Inicializa o animator.
        
        Args:
            animations: dicionário {estado: [frames]}
            initial_state: estado inicial da animação
        """
        self.animations = animations
        self.state = initial_state
        self.frame = 0.0
        self.loop = True  # Se a animação deve fazer loop

    def set_state(self, state, loop=True):
        """
        Muda o estado da animação.
        
        Args:
            state: novo estado
            loop: se a animação deve fazer loop
        """
        if self.state != state:
            self.state = state
            self.frame = 0.0
            self.loop = loop

    def update(self, speed):
        """
        Atualiza a animação e retorna o frame atual.
        
        Args:
            speed: velocidade da animação (frames por update)
            
        Returns:
            pygame.Surface: frame atual da animação
        """
        frames = self.animations[self.state]
        
        self.frame += speed
        
        if self.frame >= len(frames):
            if self.loop:
                self.frame = 0.0
            else:
                self.frame = len(frames) - 1  # Fica no último frame
        
        return frames[int(self.frame)]
    
    def is_finished(self):
        """
        Verifica se a animação terminou (apenas para animações não-loop).
        
        Returns:
            bool: True se terminou, False caso contrário
        """
        if self.loop:
            return False
        
        frames = self.animations[self.state]
        return int(self.frame) >= len(frames) - 1
    
    def reset(self):
        """Reinicia a animação atual."""
        self.frame = 0.0
