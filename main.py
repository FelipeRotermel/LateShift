"""
Ponto de entrada do jogo LateShift.
Instancia e executa a classe Game principal.
"""

import pygame
from src.game import Game

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()