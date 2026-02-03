import pygame
import sys

def test():
    print("Iniciando teste de diagnóstico...")
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("TESTE DE DIAGNÓSTICO")
        print("Janela criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar janela: {e}")
        return

    clock = pygame.time.Clock()
    count = 0
    
    while count < 300: # Corre por 5 segundos a 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill((255, 0, 0)) # Fundo Vermelho
        pygame.draw.circle(screen, (255, 255, 255), (400, 300), 50) # Círculo Branco
        pygame.display.flip()
        
        if count == 0:
            print("Primeiro frame desenhado com sucesso! Se não vês uma janela vermelha, o problema é no teu sistema.")
        
        count += 1
        clock.tick(60)
    
    print("Teste concluído.")
    pygame.quit()

if __name__ == "__main__":
    test()
