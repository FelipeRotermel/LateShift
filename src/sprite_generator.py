"""
Módulo de carregamento e montagem dos sprites dos carros.
Compõe o chassi do carro com as rodas e rotaciona as rodas em tempo real com base na velocidade.
"""

import os
import pygame
from src.constants import CAR_BALANCED, CAR_HIGH_ACCEL, CAR_TOP_SPEED

# Diretório onde as imagens dos carros estão salvas
CAR_IMAGES_DIR = os.path.join("assets", "images", "car")

# Configuração de posicionamento das rodas para cada modelo de carro
# Valores baseados na resolução original da imagem antes do redimensionamento
CAR_SPRITE_CONFIGS = {
    CAR_BALANCED: {
        "folder": "Skyline",
        "body_file": "Skyline.png",
        "wheel_file": "Wheel.png",
        "rear_x_from_left": 67,     # Pixels da borda esquerda até o centro da roda traseira
        "rear_y_from_top": 2,       # Altura do chão até a roda traseira
        "front_x_from_right": 63,   # Pixels da borda direita até o centro da roda dianteira
        "front_y_from_top": 2,      # Altura do chão até a roda dianteira
    },
    CAR_HIGH_ACCEL: {
        "folder": "Dodge",
        "body_file": "Dodge.png",
        "wheel_file": "Wheel.png",
        "rear_x_from_left": 89,
        "rear_y_from_top": 3,
        "front_x_from_right": 67,
        "front_y_from_top": 3,
    },
    CAR_TOP_SPEED: {
        "folder": "F40",
        "body_file": "F40.png",
        "wheel_file": "Wheel.png",
        "rear_x_from_left": 55,
        "rear_y_from_top": 3,
        "front_x_from_right": 72,
        "front_y_from_top": 2,
    },
}

# Alturas padrão dos carros na pista e nos menus
GAME_SPRITE_HEIGHT = 60
MENU_SPRITE_HEIGHT = 40

class CarSprite:
    """
    Representa o sprite dinâmico do carro: corpo estático e rodas que giram.
    """

    def __init__(self, body_surface, wheel_surface, rear_pos, front_pos, scale_factor):
        """
        Inicializa o sprite composto.
        :param body_surface: Superfície do corpo do carro já escalado
        :param wheel_surface: Imagem original da roda (alta resolução)
        :param rear_pos: Coordenadas (x, y) do centro da roda traseira no carro escalado
        :param front_pos: Coordenadas (x, y) do centro da roda dianteira no carro escalado
        :param scale_factor: Fator de escala aplicado ao corpo do carro
        """
        self.body = body_surface
        self.wheel_original = wheel_surface
        self.rear_pos = rear_pos
        self.front_pos = front_pos
        self.scale_factor = scale_factor

        # Ângulo acumulado das rodas (graus)
        self.wheel_angle = 0.0
        self.height = body_surface.get_height()

    def update(self, dt, speed):
        """
        Atualiza a rotação acumulada das rodas de acordo com a velocidade do carro.
        :param dt: Tempo delta do frame em segundos
        :param speed: Velocidade atual do carro (km/h)
        """
        # A velocidade de rotação é proporcional à velocidade linear do carro
        rotation_speed = speed * 8.0  # Graus por segundo por unidade de velocidade
        self.wheel_angle = (self.wheel_angle - rotation_speed * dt) % 360

    def draw(self, surface, x, y):
        """
        Desenha o chassi e as rodas giratórias sobrepostas na posição correta.
        :param surface: Superfície de destino (tela)
        :param x: Posição X superior esquerda do carro
        :param y: Posição Y superior esquerda do carro
        """
        # 1. Desenha o chassi do carro
        surface.blit(self.body, (x, y))

        # 2. Rotaciona a roda no tamanho original primeiro (para evitar wobble/tremidos)
        rotated_orig = pygame.transform.rotate(self.wheel_original, self.wheel_angle)
        row, roh = rotated_orig.get_size()

        # 3. Redimensiona a roda rotacionada para o tamanho correto de jogo
        scaled_w = int(row * self.scale_factor)
        scaled_h = int(roh * self.scale_factor)
        rotated_wheel = pygame.transform.scale(rotated_orig, (scaled_w, scaled_h))
        rot_w, rot_h = rotated_wheel.get_size()

        # Desenha a roda traseira centralizada em sua respectiva posição
        rear_cx = x + self.rear_pos[0]
        rear_cy = y + self.rear_pos[1]
        surface.blit(rotated_wheel, (rear_cx - rot_w // 2, rear_cy - rot_h // 2))

        # Desenha a roda dianteira centralizada em sua respectiva posição
        front_cx = x + self.front_pos[0]
        front_cy = y + self.front_pos[1]
        surface.blit(rotated_wheel, (front_cx - rot_w // 2, front_cy - rot_h // 2))


class SpriteGenerator:
    """
    Carrega e gerencia o carregamento de sprites do disco.
    Gera as versões de jogo (animadas) e de menu (estáticas).
    """

    def __init__(self):
        """Carrega todos os carros ao inicializar."""
        self.car_sprites = {}        # Sprites dinâmicos para a corrida
        self.car_sprites_small = {}  # Sprites estáticos simples para o menu
        self._generate_all()

    def get_sprite(self, car_type):
        """Retorna o CarSprite dinâmico correspondente ao tipo."""
        return self.car_sprites.get(car_type)

    def get_sprite_small(self, car_type):
        """Retorna o sprite de menu correspondente ao tipo."""
        return self.car_sprites_small.get(car_type)

    def _generate_all(self):
        """Carrega os arquivos de imagem de cada carro e cria os sprites escalados."""
        car_types = [CAR_BALANCED, CAR_HIGH_ACCEL, CAR_TOP_SPEED]

        for car_type in car_types:
            sprite_cfg = CAR_SPRITE_CONFIGS.get(car_type)
            if not sprite_cfg:
                continue

            folder = sprite_cfg["folder"]
            # Monta caminhos de arquivos
            body_path = os.path.join(CAR_IMAGES_DIR, folder, sprite_cfg["body_file"])
            wheel_path = os.path.join(CAR_IMAGES_DIR, folder, sprite_cfg["wheel_file"])
            placeholder_path = os.path.join(CAR_IMAGES_DIR, folder, f"{folder}Placeholder.png")

            try:
                body_img = pygame.image.load(body_path).convert_alpha()
                wheel_img = pygame.image.load(wheel_path).convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"[SpriteGenerator] Erro ao carregar imagens do {folder}: {e}")
                continue

            body_w, body_h = body_img.get_size()
            wheel_w, wheel_h = wheel_img.get_size()

            # === 1. Criação do sprite do jogo (altura fixa GAME_SPRITE_HEIGHT) ===
            scale = GAME_SPRITE_HEIGHT / body_h
            game_w = int(body_w * scale)
            game_body = pygame.transform.scale(body_img, (game_w, GAME_SPRITE_HEIGHT))

            # Calcula a posição centralizada da roda traseira no corpo escalado
            rear_cx = int((sprite_cfg["rear_x_from_left"] + wheel_w / 2) * scale)
            rear_cy = int((body_h - sprite_cfg["rear_y_from_top"] - wheel_h / 2) * scale)

            # Calcula a posição centralizada da roda dianteira no corpo escalado
            front_cx = int((body_w - sprite_cfg["front_x_from_right"] - wheel_w / 2) * scale)
            front_cy = int((body_h - sprite_cfg["front_y_from_top"] - wheel_h / 2) * scale)

            # Instancia o CarSprite do jogo
            self.car_sprites[car_type] = CarSprite(
                game_body, wheel_img,
                rear_pos=(rear_cx, rear_cy),
                front_pos=(front_cx, front_cy),
                scale_factor=scale
            )

            # === 2. Criação do sprite estático do menu (com as rodas já inclusas) ===
            try:
                placeholder_img = pygame.image.load(placeholder_path).convert_alpha()
            except (pygame.error, FileNotFoundError):
                # Caso não tenha o placeholder estático, usa o chassi padrão como fallback
                placeholder_img = body_img

            p_w, p_h = placeholder_img.get_size()
            menu_scale = MENU_SPRITE_HEIGHT / p_h
            menu_w = int(p_w * menu_scale)
            menu_surf = pygame.transform.scale(placeholder_img, (menu_w, MENU_SPRITE_HEIGHT))

            self.car_sprites_small[car_type] = menu_surf
