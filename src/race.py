"""
Módulo da pista de corrida e renderização do cenário
Controla o efeito de parallax nas imagens do plano de fundo e o desenho da pista
"""

import os
import random
import pygame
from src.constants import (
    SCREEN_WIDTH, TRACK_HEIGHT, NEON_YELLOW,
    NEON_RED, NEON_GREEN, BLACK, WHITE, GRAY_MED, STAGE_CONFIGS
)

# Caminho base dos recursos de imagem
IMAGES_BASE_DIR = os.path.join("assets", "images")

# Dicionário que mapeia o índice do estágio (0 a 5) para a sua pasta de imagens correspondente
STAGE_CITY_MAP = {
    0: "city 5",
    1: "city 3",
    2: "city 2",
    3: "city 8",
    4: "city 6",
    5: "city 1",
}

class Race:
    """
    Gerencia a renderização do cenário e do asfalto com efeito parallax
    Desenha os competidores (jogador e IA) de forma sincronizada na tela
    """

    def __init__(self):
        """Inicializa fontes de texto e variáveis de scroll da pista"""
        self.stage_index = 0
        self.stage_config = STAGE_CONFIGS[0]
        self.parallax_offset = 0.0

        # Listas para armazenar as superfícies das camadas de cenário
        self._layers = []
        self._layer_widths = []

        # Fontes de texto
        self.font_large = pygame.font.Font(None, 120)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 28)

    def set_stage(self, stage_index):
        """
        Configura o estágio atual e carrega as imagens do cenário
        :param stage_index: Índice da fase (0 a 5)
        """
        self.stage_index = stage_index
        self.stage_config = STAGE_CONFIGS[stage_index]
        self.parallax_offset = 0.0
        self._load_parallax_layers()

    def reset(self):
        """Reseta a posição do cenário para o início"""
        self.parallax_offset = 0.0

    def update(self, dt, player_speed, ai_speed):
        """
        Avança a posição do cenário conforme a velocidade do jogador
        :param dt: Tempo delta em segundos
        :param player_speed: Velocidade do jogador (km/h)
        :param ai_speed: Velocidade da IA (km/h)
        """
        # O cenário se move com base na velocidade do jogador para dar a sensação correta de movimento
        self.parallax_offset += player_speed * dt * 5.0

    def draw_track(self, surface, player_car, ai_car, player_sprite, ai_sprite):
        """
        Renderiza todo o background, asfalto, linha de chegada e os carros
        :param surface: Tela do Pygame
        """
        cfg = self.stage_config

        self._draw_parallax_layers(surface)

        self._draw_road(surface, cfg)

        self._draw_finish_line(surface, player_car, ai_car)

        self._draw_cars(surface, player_car, ai_car, player_sprite, ai_sprite)

    def draw_countdown(self, surface, count):
        """
        Desenha os números de contagem regressiva na tela
        """
        if count > 0:
            text = self.font_large.render(str(count), True, NEON_RED)
        else:
            text = self.font_large.render("GO!", True, NEON_GREEN)

        shadow = self.font_large.render(str(count) if count > 0 else "GO!", True, BLACK)

        sx = SCREEN_WIDTH // 2 - text.get_width() // 2
        sy = TRACK_HEIGHT // 2 - text.get_height() // 2

        # Desenha com efeito de sombra simples
        surface.blit(shadow, (sx + 3, sy + 3))
        surface.blit(text, (sx, sy))

    def draw_result(self, surface, won, engine_blown=False):
        """
        Desenha a tela de resultado da corrida por cima da pista
        """
        overlay = pygame.Surface((SCREEN_WIDTH, TRACK_HEIGHT), pygame.SRCALPHA)
        if won:
            overlay.fill((0, 40, 0, 160))  # Verde semi-transparente
        else:
            overlay.fill((40, 0, 0, 160))  # Vermelho semi-transparente
        surface.blit(overlay, (0, 0))

        if won:
            title = self.font_large.render("Vitória!", True, NEON_GREEN)
            sub = self.font_medium.render("Você cruzou a linha de chegada primeiro!", True, WHITE)
        else:
            title = self.font_large.render("Derrota!", True, NEON_RED)
            if engine_blown:
                sub = self.font_medium.render("O motor explodiu!", True, NEON_YELLOW)
            else:
                sub = self.font_medium.render("Seu oponente cruzou a linha de chegada primeiro!", True, WHITE)

        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, TRACK_HEIGHT // 2 - 60))
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, TRACK_HEIGHT // 2 + 10))

        hint = self.font_small.render("Pressione ESPAÇO para retornar ao menu", True, GRAY_MED)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, TRACK_HEIGHT // 2 + 70))

    def _load_parallax_layers(self):
        """Carrega e escala as camadas PNG da pasta correspondente à fase"""
        self._layers = []
        self._layer_widths = []

        city_folder = STAGE_CITY_MAP.get(self.stage_index, "city 1")
        city_path = os.path.join(IMAGES_BASE_DIR, city_folder)

        # Lista e ordena os arquivos numéricos de 1 a N.png
        png_files = []
        for f in os.listdir(city_path):
            if f.lower().endswith(".png"):
                name = os.path.splitext(f)[0]
                try:
                    num = int(name)
                    png_files.append((num, f))
                except ValueError:
                    pass
        png_files.sort(key=lambda x: x[0])

        target_h = TRACK_HEIGHT

        for num, filename in png_files:
            filepath = os.path.join(city_path, filename)
            img = pygame.image.load(filepath).convert_alpha()
            orig_w, orig_h = img.get_size()

            # Escala a imagem mantendo a proporção original para preencher a pista
            scale_factor = target_h / orig_h
            new_w = int(orig_w * scale_factor)
            scaled = pygame.transform.scale(img, (new_w, target_h))

            self._layers.append(scaled)
            self._layer_widths.append(new_w)

    def _draw_parallax_layers(self, surface):
        """Renderiza cada camada do cenário com uma velocidade diferente para criar profundidade"""
        if not self._layers:
            surface.fill((20, 20, 40), (0, 0, SCREEN_WIDTH, TRACK_HEIGHT))
            return

        num_layers = len(self._layers)

        for i, (layer, layer_w) in enumerate(zip(self._layers, self._layer_widths)):
            # Camadas mais distantes (céu) se movem devagar (0.05). Camadas frontais se movem rápido (0.8)
            if num_layers > 1:
                speed_factor = 0.05 + (i / (num_layers - 1)) * 0.75
            else:
                speed_factor = 0.1

            # Wrap das imagens (efeito infinito)
            offset = (self.parallax_offset * speed_factor) % layer_w
            x = -offset
            while x < SCREEN_WIDTH:
                surface.blit(layer, (int(x), 0))
                x += layer_w

    def _draw_road(self, surface, cfg):
        """Desenha a estrada e as listras divisórias amarelas ondulantes"""
        road_y = TRACK_HEIGHT - 100
        road_h = 100

        # Faixa de chão verde/terra
        pygame.draw.rect(surface, cfg["ground_color"], (0, road_y, SCREEN_WIDTH, 15))

        # Asfalto
        pygame.draw.rect(surface, cfg["road_color"], (0, road_y + 15, SCREEN_WIDTH, road_h - 15))

        # Faixas centrais pontilhadas (se movem à velocidade de 1.0x da pista)
        dash_offset = self.parallax_offset % 80
        line_y = road_y + 55
        for i in range(-1, SCREEN_WIDTH // 80 + 2):
            dx = i * 80 - dash_offset
            pygame.draw.rect(surface, cfg["road_line"], (dx, line_y, 40, 4))

        # Listras sólidas das laterais do asfalto
        pygame.draw.rect(surface, cfg["road_line"], (0, road_y + 15, SCREEN_WIDTH, 2))
        pygame.draw.rect(surface, cfg["road_line"], (0, road_y + road_h - 2, SCREEN_WIDTH, 2))

    def _draw_finish_line(self, surface, player_car, ai_car):
        """Desenha o grid xadrez da linha de chegada quando os carros estão próximos"""
        # Distância que falta para o jogador cruzar a linha
        stage_distance = self.stage_config["distance"]
        remaining = stage_distance - player_car.distance
        
        # Converte a distância lógica do jogo para posição em pixels na tela
        finish_screen_x = remaining * 3.0 + 200

        if 0 <= finish_screen_x <= SCREEN_WIDTH + 50:
            road_y = TRACK_HEIGHT - 100
            sq_size = 8

            # Desenha padrão xadrez (quadriculado) de corrida
            for row in range(12):
                for col in range(3):
                    color = WHITE if (row + col) % 2 == 0 else BLACK
                    pygame.draw.rect(
                        surface, color,
                        (finish_screen_x + col * sq_size,
                        road_y + 16 + row * sq_size,
                        sq_size, sq_size)
                    )

    def _draw_cars(self, surface, player_car, ai_car, player_sprite, ai_sprite):
        """Desenha os sprites dos carros baseados na distância relativa entre eles"""
        road_y = TRACK_HEIGHT - 100

        # Jogador fica travado na posição horizontal fixa (x=200)
        player_screen_x = 200
        
        # A IA avança ou recua livremente no scroll de acordo com a escala de 3.0 pixels/unidade
        ai_relative_dist = ai_car.distance - player_car.distance
        ai_screen_x = 200 + ai_relative_dist * 3.0

        player_lane_bottom = road_y + 95  # Pista inferior
        ai_lane_bottom = road_y + 55      # Pista superior

        # Desenha a IA
        if ai_sprite:
            sh = ai_sprite.height if hasattr(ai_sprite, 'height') else ai_sprite.get_height()
            ay = ai_lane_bottom - sh
            if hasattr(ai_sprite, 'draw'):
                ai_sprite.draw(surface, int(ai_screen_x), ay)
            else:
                surface.blit(ai_sprite, (int(ai_screen_x), ay))
        else:
            # Fallback retangular caso falte o sprite
            pygame.draw.rect(surface, (200, 50, 50), (int(ai_screen_x), ai_lane_bottom - 30, 120, 30))

        # Desenha o Jogador
        if player_sprite:
            sh = player_sprite.height if hasattr(player_sprite, 'height') else player_sprite.get_height()
            py = player_lane_bottom - sh
            if hasattr(player_sprite, 'draw'):
                player_sprite.draw(surface, int(player_screen_x), py)
            else:
                surface.blit(player_sprite, (int(player_screen_x), py))
        else:
            pygame.draw.rect(surface, (50, 150, 255), (int(player_screen_x), player_lane_bottom - 30, 120, 30))

        # Se o motor explodiu, desenha partículas de fumaça cinza na traseira do carro
        if player_car.engine_blown:
            for _ in range(5):
                sx = player_screen_x + random.randint(20, 80)
                sy = player_lane_bottom + random.randint(-20, 5)
                sr = random.randint(4, 12)

                smoke_col = random.choice([(60, 60, 60), (80, 80, 80), (40, 40, 40)])
                pygame.draw.circle(surface, smoke_col, (sx, sy), sr)
