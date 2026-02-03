import pygame
import os

class SpriteSheet:
    """
    Classe para carregar e extrair frames de uma spritesheet.
    """
    def __init__(self, path, frame_w, frame_h):
        """
        Inicializa a spritesheet.
        
        Args:
            path: caminho para o ficheiro da spritesheet
            frame_w: largura de cada frame
            frame_h: altura de cada frame
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Spritesheet não encontrada: {path}")
        
        self.sheet = pygame.image.load(path).convert_alpha()
        self.fw = frame_w
        self.fh = frame_h

    def get_row(self, row, frames):
        """
        Extrai uma linha de frames da spritesheet.
        
        Args:
            row: índice da linha (começa em 0)
            frames: número de frames a extrair
            
        Returns:
            list: lista de superfícies pygame (frames)
        """
        return [
            self.sheet.subsurface((i * self.fw, row * self.fh, self.fw, self.fh))
            for i in range(frames)
        ]

    def get_grid(self, rows, cols):
        """
        Extrai todos os frames de uma grid.
        
        Args:
            rows: número de linhas
            cols: número de colunas
            
        Returns:
            list: lista de superfícies pygame (frames)
        """
        frames = []
        for r in range(rows):
            for c in range(cols):
                frames.append(
                    self.sheet.subsurface((c * self.fw, r * self.fh, self.fw, self.fh))
                )
        return frames
    
    def get_frame(self, col, row):
        """
        Extrai um único frame específico.
        
        Args:
            col: coluna do frame
            row: linha do frame
            
        Returns:
            pygame.Surface: frame extraído
        """
        return self.sheet.subsurface((col * self.fw, row * self.fh, self.fw, self.fh))
