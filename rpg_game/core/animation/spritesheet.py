import pygame
import os

class SpriteSheet:
    def __init__(self, path, frame_w, frame_h):
        self.fw = frame_w
        self.fh = frame_h
        
        if not os.path.exists(path):
            # Tentar remover o .png duplicado se existir
            alt_path = path.replace(".png.png", ".png")
            if os.path.exists(alt_path):
                path = alt_path
            else:
                print(f"AVISO: Ficheiro não encontrado: {path}")
                self.sheet = pygame.Surface((frame_w, frame_h))
                self.sheet.fill((255, 0, 255)) # Rosa choque para indicar erro
                return

        try:
            self.sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Erro ao carregar {path}: {e}")
            self.sheet = pygame.Surface((frame_w, frame_h))
            self.sheet.fill((255, 0, 255))

    def get_row(self, row, frames):
        try:
            return [
                self.sheet.subsurface((i * self.fw, row * self.fh, self.fw, self.fh))
                for i in range(frames)
            ]
        except:
            return [pygame.Surface((self.fw, self.fh)) for _ in range(frames)]

    def get_grid(self, rows, cols):
        frames = []
        for r in range(rows):
            for c in range(cols):
                try:
                    frames.append(self.sheet.subsurface((c * self.fw, r * self.fh, self.fw, self.fh)))
                except:
                    frames.append(pygame.Surface((self.fw, self.fh)))
        return frames
    
    def get_frame(self, col, row):
        try:
            return self.sheet.subsurface((col * self.fw, row * self.fh, self.fw, self.fh))
        except:
            return pygame.Surface((self.fw, self.fh))
