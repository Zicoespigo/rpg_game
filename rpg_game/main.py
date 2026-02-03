import pygame
import sys
import os
import traceback

# Sistema de Log para diagnóstico
def log_error(msg):
    with open("erro_log.txt", "a") as f:
        f.write(msg + "\n")

if os.path.exists("erro_log.txt"): os.remove("erro_log.txt")
log_error("Iniciando Manus RPG v1.8.1...")

try:
    from core.settings import *
    from core.game import Game
    from core.ui_manager import MenuManager
    log_error("Importações concluídas.")
except Exception as e:
    log_error(f"Erro nas importações: {traceback.format_exc()}")

# Inicialização do Pygame
try:
    pygame.init()
    try:
        pygame.mixer.init()
        log_error("Mixer de áudio iniciado.")
    except:
        log_error("Aviso: Mixer de áudio falhou.")
    log_error("Pygame iniciado.")
except Exception as e:
    log_error(f"Erro ao iniciar Pygame: {traceback.format_exc()}")

# Configuração de Janela
try:
    screen = pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF)
    pygame.display.set_caption("Manus RPG - v1.8.1")
    clock = pygame.time.Clock()
    log_error("Janela criada.")
except Exception as e:
    log_error(f"Erro ao criar janela: {traceback.format_exc()}")

try:
    ui = MenuManager(screen)
    game = None 
    log_error("MenuManager criado.")
except Exception as e:
    log_error(f"Erro ao criar MenuManager: {traceback.format_exc()}")

# Inicia música do menu
ui.play_menu_music()

log_error("Entrando no loop principal...")

try:
    while True:
        clock.tick(60)
        events = pygame.event.get()
        
        player_ref = game.player if (game and hasattr(game, 'player')) else None
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            action = ui.handle_event(event, player_ref)
            
            if action == "NEW_GAME":
                log_error("Iniciando novo jogo...")
                game = Game(screen)
                ui.state = "PLAYING"
                ui.play_game_music()
            elif action == "MAIN_MENU":
                ui.state = "MAIN_MENU"
                game = None
                ui.play_menu_music()
            elif action == "EXIT":
                pygame.quit()
                sys.exit()

        # Desenho
        screen.fill((0, 0, 0))
        
        if ui.state == "PLAYING" and game:
            game.update()
            game.draw()
        elif ui.state == "PAUSED" and game:
            game.draw()
            ui.draw()
        elif ui.state == "SKILL_TREE" and game:
            game.draw()
            ui.draw(player_ref)
        else:
            ui.draw(player_ref)

        pygame.display.flip()

except Exception as e:
    log_error(f"Erro no loop principal: {traceback.format_exc()}")
    pygame.quit()
    sys.exit()
