"""
Módulo de menus
Implementa o menu principal, seleção de carro e seleção de fase de forma didática
"""

import math
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CAR_BALANCED, CAR_HIGH_ACCEL, CAR_TOP_SPEED,
    CAR_CONFIGS, STAGE_CONFIGS, WHITE, DARK_BG, NEON_CYAN, NEON_GREEN, NEON_ORANGE,
    NEON_RED, NEON_YELLOW, GEAR_COLORS, GEAR_FIRST, GEAR_SECOND, GEAR_THIRD, GEAR_FOURTH, GEAR_FIFTH, GEAR_SIXTH,
    GRAY_LIGHT, GRAY_MED, GRAY_DARK
)

class MainMenu:
    """
    Menu principal com o título, opções de navegação e painel explicativo de controles
    """

    def __init__(self):
        """Inicializa fontes de texto e cronômetro de animação"""
        self.font_title = pygame.font.Font(None, 90)
        self.font_subtitle = pygame.font.Font(None, 44)
        self.font_option = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 26)
        self.font_tiny = pygame.font.Font(None, 22)
        self._anim_timer = 0.0

    def update(self, dt):
        """
        Atualiza animações do menu
        :param dt: Tempo delta em segundos
        """
        self._anim_timer += dt

    def draw(self, surface):
        """
        Desenha o menu principal completo
        :param surface: Tela do Pygame
        """
        surface.fill(DARK_BG)

        self._draw_bg_lines(surface)

        self._draw_title(surface)

        self._draw_options(surface)

        self._draw_controls_panel(surface)

    def _draw_bg_lines(self, surface):
        """Desenha linhas de fundo onduladas"""
        for i in range(0, SCREEN_WIDTH, 60):
            offset = math.sin(self._anim_timer * 0.5 + i * 0.02) * 20
            color = (20, 20, 35)
            pygame.draw.line(surface, color, (i, 0), (i + int(offset), SCREEN_HEIGHT), 1)

    def _draw_title(self, surface):
        """Desenha o título e o subtítulo com efeito pulsante"""
        pulse = 0.85 + 0.15 * math.sin(self._anim_timer * 2)
        title_color = tuple(int(c * pulse) for c in NEON_ORANGE)

        # Efeito de sombra
        shadow = self.font_title.render("LateShift", True, (40, 25, 10))
        title = self.font_title.render("LateShift", True, title_color)

        tx = SCREEN_WIDTH // 2 - title.get_width() // 2
        surface.blit(shadow, (tx + 3, 63))
        surface.blit(title, (tx, 60))

        sub = self.font_subtitle.render("DRAG RACING", True, GRAY_MED)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 145))

        # Faixa separadora
        line_w = 300
        lx = SCREEN_WIDTH // 2 - line_w // 2
        pygame.draw.rect(surface, NEON_ORANGE, (lx, 185, line_w, 2))

    def _draw_options(self, surface):
        """Desenha as caixas com opções de menu"""
        options = [
            ("[1]  Selecionar corrida", NEON_GREEN),
            ("[2]  Selecionar carro", NEON_CYAN),
            ("[3]  Sair", NEON_RED),
        ]

        for i, (text, color) in enumerate(options):
            y = 220 + i * 60
            opt_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, y - 5, 360, 45)
            pygame.draw.rect(surface, (20, 20, 30), opt_rect)
            pygame.draw.rect(surface, color, opt_rect, 2)

            opt = self.font_option.render(text, True, color)
            surface.blit(opt, (SCREEN_WIDTH // 2 - opt.get_width() // 2, y + 5))

    def _draw_controls_panel(self, surface):
        """Desenha o painel de explicações dos controles na parte inferior"""
        panel_x = 60
        panel_y = 430
        panel_w = SCREEN_WIDTH - 120
        panel_h = 260

        pygame.draw.rect(surface, (15, 15, 25), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, GRAY_DARK, (panel_x, panel_y, panel_w, panel_h), 2)

        ctrl_title = self.font_small.render("CONTROLES", True, NEON_YELLOW)
        surface.blit(ctrl_title, (panel_x + 15, panel_y + 10))

        # Coluna da esquerda: pedais básicos
        left_x = panel_x + 20
        y = panel_y + 40

        controls = [
            ("[W]", "Acelerar", NEON_GREEN),
            ("[SPACE]", "Embreagem (segure durante as trocas)", NEON_CYAN),
            ("[Arrows]", "Troca de marcha (Padrão H)", NEON_ORANGE),
        ]

        for key, desc, color in controls:
            key_render = self.font_small.render(key, True, color)
            desc_render = self.font_tiny.render(f"  {desc}", True, GRAY_LIGHT)
            surface.blit(key_render, (left_x, y))
            surface.blit(desc_render, (left_x + key_render.get_width() + 5, y + 3))
            y += 28

        # Coluna da direita: sequências de câmbio
        right_x = panel_x + panel_w // 2 + 20
        y = panel_y + 40

        hp_title = self.font_small.render("Padrão de marchas (H-Pattern):", True, NEON_YELLOW)
        surface.blit(hp_title, (right_x, y))
        y += 30

        shifts = [
            ("N -> 1st:", "SPC + <- ^", GEAR_COLORS[GEAR_FIRST]),
            ("1st -> 2nd:", "SPC + v v", GEAR_COLORS[GEAR_SECOND]),
            ("2nd -> 3rd:", "SPC + ^ -> ^", GEAR_COLORS[GEAR_THIRD]),
            ("3rd -> 4th:", "SPC + v v", GEAR_COLORS[GEAR_FOURTH]),
            ("4th -> 5th:", "SPC + ^ -> ^", GEAR_COLORS[GEAR_FIFTH]),
            ("5th -> 6th:", "SPC + v v", GEAR_COLORS[GEAR_SIXTH]),
        ]

        for label, keys, color in shifts:
            lbl = self.font_tiny.render(label, True, GRAY_LIGHT)
            kys = self.font_tiny.render(f"  {keys}", True, color)
            surface.blit(lbl, (right_x, y))
            surface.blit(kys, (right_x + lbl.get_width() + 2, y))
            y += 22

        y += 4
        err = self.font_tiny.render("Não é possível passar a marcha sem a embreagem! SPACE", True, NEON_RED)
        surface.blit(err, (right_x, y))

        # Mini diagrama H-Pattern decorativo
        hx = panel_x + 200
        hy = panel_y + 210
        sp = 18

        pygame.draw.line(surface, GRAY_MED, (hx - 3*sp, hy), (hx + 3*sp, hy), 2)
        pygame.draw.line(surface, GRAY_MED, (hx - 3*sp, hy), (hx - 3*sp, hy - sp), 2)  # R
        pygame.draw.line(surface, GRAY_MED, (hx - sp, hy - sp), (hx - sp, hy + sp), 2)  # 1/2
        pygame.draw.line(surface, GRAY_MED, (hx + sp, hy - sp), (hx + sp, hy + sp), 2)  # 3/4
        pygame.draw.line(surface, GRAY_MED, (hx + 3*sp, hy - sp), (hx + 3*sp, hy + sp), 2)  # 5/6

        labels = [
            ("R", -3*sp, -sp), ("1", -sp, -sp), ("3", sp, -sp), ("5", 3*sp, -sp),
            ("N", sp, 0),
            ("2", -sp, sp), ("4", sp, sp), ("6", 3*sp, sp),
        ]
        for lbl, dx, dy in labels:
            t = self.font_tiny.render(lbl, True, WHITE)
            surface.blit(t, (hx + dx - t.get_width() // 2, hy + dy - t.get_height() // 2))


class CarSelectMenu:
    """
    Menu para a seleção do modelo de carro com exibição dos atributos técnicos
    """

    def __init__(self, sprite_generator):
        """
        Inicializa o menu de seleção
        :param sprite_generator: Objeto SpriteGenerator para puxar a imagem estática dos carros
        """
        self.sprite_gen = sprite_generator
        self.selected_index = 0
        self.font_title = pygame.font.Font(None, 64)
        self.font_name = pygame.font.Font(None, 40)
        self.font_stat = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)
        self._anim_timer = 0.0

    def update(self, dt):
        """Atualiza animações do menu"""
        self._anim_timer += dt

    def draw(self, surface, selected_index):
        """
        Renderiza a tela de seleção de carros
        :param surface: Tela do Pygame
        :param selected_index: Índice do carro selecionado
        """
        self.selected_index = selected_index
        surface.fill(DARK_BG)

        # Título da tela
        title = self.font_title.render("SELECT CAR", True, NEON_ORANGE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
        pygame.draw.rect(surface, NEON_ORANGE, (SCREEN_WIDTH // 2 - 150, 95, 300, 2))

        # Desenha os cards de carros disponíveis
        car_types = [CAR_BALANCED, CAR_HIGH_ACCEL, CAR_TOP_SPEED]
        for i, car_type in enumerate(car_types):
            config = CAR_CONFIGS[car_type]
            y = 130 + i * 180
            is_selected = (i == selected_index)
            self._draw_car_card(surface, config, car_type, i, y, is_selected)

        # Dica rápida de teclado
        hint = self.font_small.render("Pressione [1-3] para selecionar  |  [ESC] para voltar", True, GRAY_MED)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))

    def _draw_car_card(self, surface, config, car_type, index, y, selected):
        """Desenha um card retangular com dados e o sprite do carro"""
        card_x = 100
        card_w = SCREEN_WIDTH - 200
        card_h = 155

        # Cor de fundo destaca o selecionado
        bg_color = (25, 25, 40) if not selected else (30, 35, 55)
        pygame.draw.rect(surface, bg_color, (card_x, y, card_w, card_h))
        border_color = NEON_GREEN if selected else GRAY_DARK
        pygame.draw.rect(surface, border_color, (card_x, y, card_w, card_h), 3 if selected else 1)

        # Número para atalho
        num = self.font_name.render(f"[{index + 1}]", True, NEON_GREEN if selected else GRAY_MED)
        surface.blit(num, (card_x + 15, y + 15))

        # Desenha a foto de preview do carro
        sprite = self.sprite_gen.get_sprite_small(car_type)
        if sprite:
            sw, sh = sprite.get_size()
            preview_area_x = card_x + 70
            preview_area_w = 150
            preview_area_cy = y + card_h // 2 + 10
            sprite_x = preview_area_x + (preview_area_w - sw) // 2
            sprite_y = preview_area_cy - sh // 2
            surface.blit(sprite, (sprite_x, sprite_y))

        # Nome do carro (com sua classificação/descrição curta)
        name_text = f"{config['name']} ({config['desc']})"
        name = self.font_name.render(name_text, True, WHITE)
        surface.blit(name, (card_x + 230, y + 15))

        # Descrição
        desc = self.font_stat.render(config["description"], True, GRAY_LIGHT)
        surface.blit(desc, (card_x + 230, y + 50))

        # Barras de atributos proporcional ao máximo real de cada atributo
        stats = [
            ("Velocidade", config["top_speed"] / 310.0, NEON_CYAN),
            ("Aceleração", config["acceleration"] / 1.35, NEON_GREEN),
            ("Torque", config["torque"] / 1.25, NEON_ORANGE),
        ]

        for j, (label, value, color) in enumerate(stats):
            sy = y + 80 + j * 22
            lbl = self.font_small.render(f"{label}:", True, GRAY_MED)
            surface.blit(lbl, (card_x + 230, sy))

            # Fundo da barra
            bar_x = card_x + 340
            bar_w = 300
            bar_h = 12
            pygame.draw.rect(surface, GRAY_DARK, (bar_x, sy + 3, bar_w, bar_h))

            # Preenchimento proporcional
            fill_w = int(bar_w * min(1.0, value))
            pygame.draw.rect(surface, color, (bar_x, sy + 3, fill_w, bar_h))
            pygame.draw.rect(surface, GRAY_MED, (bar_x, sy + 3, bar_w, bar_h), 1)


class StageSelectMenu:
    """
    Menu para a seleção do estágio da corrida
    Carrega previews dinâmicos das imagens do background
    """

    def __init__(self):
        """Inicializa fontes e carrega imagens de visualização prévia da fase"""
        self.font_title = pygame.font.Font(None, 64)
        self.font_stage = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.font_tiny = pygame.font.Font(None, 22)
        self._anim_timer = 0.0

        # Dicionário {indice: imagem_pygame} das fotos das cidades
        self._previews = self._load_previews()

    def _load_previews(self):
        """Tenta carregar o céu (1.png) de cada pasta de cidade para desenhar de thumbnail"""
        import os
        from src.race import STAGE_CITY_MAP, IMAGES_BASE_DIR

        previews = {}
        preview_w = 496
        preview_h = 65

        for stage_idx, city_folder in STAGE_CITY_MAP.items():
            city_path = os.path.join(IMAGES_BASE_DIR, city_folder)
            img_path = os.path.join(city_path, "1.png")
            img = pygame.image.load(img_path).convert_alpha()
            previews[stage_idx] = pygame.transform.scale(img, (preview_w, preview_h))
        return previews

    def update(self, dt):
        """Atualiza animações do menu"""
        self._anim_timer += dt

    def draw(self, surface):
        """
        Desenha o menu de fases em formato de grid
        :param surface: Tela do Pygame
        """
        surface.fill(DARK_BG)

        # Título da tela
        title = self.font_title.render("Selecionar fase", True, NEON_ORANGE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        pygame.draw.rect(surface, NEON_ORANGE, (SCREEN_WIDTH // 2 - 150, 82, 300, 2))

        # Grid (3 linhas x 2 colunas)
        for i, stage in enumerate(STAGE_CONFIGS):
            col = i % 2
            row = i // 2
            x = 100 + col * 560
            y = 110 + row * 190

            self._draw_stage_card(surface, stage, i, x, y)

        hint = self.font_small.render("Pressione [1-6] para selecionar  |  [ESC] para voltar", True, GRAY_MED)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 35))

    def _draw_stage_card(self, surface, stage, index, x, y):
        """Desenha cada quadrado de estágio contendo o preview do cenário e dificuldade da IA"""
        w, h = 500, 165
        pygame.draw.rect(surface, (20, 20, 30), (x, y, w, h))

        # Desenha a foto ou um gradiente padrão caso falhe ao carregar
        preview_h = 65
        if index in self._previews:
            surface.blit(self._previews[index], (x + 2, y + 2))
        else:
            # Fallback
            top = stage.get("sky_top", (40, 40, 80))
            bot = stage.get("sky_bottom", (80, 80, 120))
            for py in range(preview_h):
                t = py / max(1, preview_h - 1)
                color = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
                pygame.draw.line(surface, color, (x + 2, y + 2 + py), (x + w - 2, y + 2 + py))

        # Moldura preta fina
        pygame.draw.rect(surface, GRAY_DARK, (x, y, w, h), 2)

        # Dados em texto da fase
        num = self.font_stage.render(f"[{index + 1}]", True, NEON_GREEN)
        surface.blit(num, (x + 12, y + preview_h + 12))

        name = self.font_stage.render(stage["name"], True, WHITE)
        surface.blit(name, (x + 60, y + preview_h + 12))

        desc = self.font_small.render(stage["desc"], True, GRAY_MED)
        surface.blit(desc, (x + 60, y + preview_h + 42))

        # Medidor visual de dificuldade da IA
        diff = stage["ai_multiplier"]
        if diff <= 0.62:
            diff_color = NEON_GREEN
            diff_label = "Easy"
        elif diff <= 0.66:
            diff_color = NEON_YELLOW
            diff_label = "Medium"
        elif diff <= 0.72:
            diff_color = NEON_ORANGE
            diff_label = "Hard"
        else:
            diff_color = NEON_RED
            diff_label = "Extreme"

        diff_text = self.font_small.render(f"AI: {diff:.2f}x ({diff_label})", True, diff_color)
        surface.blit(diff_text, (x + 60, y + preview_h + 68))

        # Desenha a barra da dificuldade da IA
        bar_x = x + 250
        bar_y = y + preview_h + 72
        bar_w = 200
        bar_h = 10
        pygame.draw.rect(surface, GRAY_DARK, (bar_x, bar_y, bar_w, bar_h))

        # Calcula preenchimento proporcional (0.60 -> 25%, 0.75 -> 100%)
        progress = max(0.0, min(1.0, (diff - 0.55) / 0.20))
        fill = int(bar_w * progress)
        pygame.draw.rect(surface, diff_color, (bar_x, bar_y, fill, bar_h))
        pygame.draw.rect(surface, GRAY_MED, (bar_x, bar_y, bar_w, bar_h), 1)
