"""
Módulo do painel de instrumentos (Dashboard)
Renderiza o velocímetro, conta-giros, marcha engatada, pedais de controle e o layout do H-Patter
"""

import math
import pygame
from src.constants import (
    SCREEN_WIDTH, DASHBOARD_Y, DASHBOARD_HEIGHT, GEAR_NEUTRAL,
    GEAR_REVERSE, GEAR_FIRST, GEAR_SECOND, GEAR_THIRD, GEAR_FOURTH,
    GEAR_FIFTH, GEAR_SIXTH, GEAR_COLORS, RPM_MAX, RPM_REDLINE,
    H_PATTERN_POSITIONS, WHITE, NEON_RED, NEON_GREEN, NEON_ORANGE,
    NEON_YELLOW, NEON_CYAN, DASHBOARD_BG, DASHBOARD_BORDER, GAUGE_BG,
    GAUGE_RING, PEDAL_IDLE, PEDAL_GAS_ACTIVE, PEDAL_CLUTCH_ACTIVE,
    GRAY_MED, GRAY_DARK
)

class Dashboard:
    """
    Desenha o painel na parte inferior da tela contendo as informações de telemetria
    e a visualização de embreagem/acelerador/câmbio
    """

    def __init__(self):
        """Inicializa as fontes e timers de animação do painel"""
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.font_tiny = pygame.font.Font(None, 20)
        self.font_gear = pygame.font.Font(None, 80)

        # Timer para piscar luzes e elementos de aviso
        self._anim_timer = 0.0

    def update(self, dt):
        """
        Atualiza animações do painel
        :param dt: Tempo delta em segundos
        """
        self._anim_timer += dt

    def draw(self, surface, car, shifter):
        """
        Desenha todos os sub-elementos do painel na tela de corrida
        :param surface: Tela do Pygame
        :param car: Objeto Car do jogador
        :param shifter: Objeto Shifter do jogador
        """
        panel_y = DASHBOARD_Y
        panel_h = DASHBOARD_HEIGHT

        self._draw_panel_background(surface, panel_y, panel_h)

        self._draw_speedometer(surface, 140, panel_y + 110, 80, car)

        self._draw_tachometer(surface, 340, panel_y + 110, 80, car)

        self._draw_gear_indicator(surface, 510, panel_y + 30, car, shifter)

        self._draw_h_pattern_display(surface, 700, panel_y + 30, shifter)

        self._draw_pedals(surface, 920, panel_y + 40, car)

        self._draw_shift_hints(surface, 1070, panel_y + 30, shifter)

    def _draw_panel_background(self, surface, y, h):
        """Desenha a faixa escura do painel e sua divisória com neon cyan"""
        pygame.draw.rect(surface, DASHBOARD_BG, (0, y, SCREEN_WIDTH, h))
        pygame.draw.rect(surface, DASHBOARD_BORDER, (0, y, SCREEN_WIDTH, 3))
        pygame.draw.rect(surface, NEON_CYAN, (0, y, SCREEN_WIDTH, 1))

    def _draw_speedometer(self, surface, cx, cy, radius, car):
        """Desenha o velocímetro de agulha"""
        # Fundo escuro e círculo limitador
        pygame.draw.circle(surface, GAUGE_BG, (cx, cy), radius)
        pygame.draw.circle(surface, GAUGE_RING, (cx, cy), radius, 3)

        # Desenha os pauzinhos de marcação de velocidade
        for i in range(0, 11):
            angle = math.radians(-225 + i * 27)
            inner = radius - 12
            outer = radius - 4
            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner
            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer
            color = WHITE if i < 8 else NEON_RED
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)

        # Calcula o ângulo da agulha proporcional à velocidade atual
        speed_frac = min(1.0, car.speed / max(1, car.top_speed))
        needle_angle = math.radians(-225 + speed_frac * 270)
        needle_len = radius - 18
        nx = cx + math.cos(needle_angle) * needle_len
        ny = cy + math.sin(needle_angle) * needle_len
        pygame.draw.line(surface, NEON_CYAN, (cx, cy), (nx, ny), 3)
        pygame.draw.circle(surface, WHITE, (cx, cy), 5)

        # Desenha o texto de velocidade digital
        speed_text = self.font_medium.render(f"{int(car.speed)}", True, WHITE)
        surface.blit(speed_text, (cx - speed_text.get_width() // 2, cy + 25))
        unit = self.font_tiny.render("km/h", True, GRAY_MED)
        surface.blit(unit, (cx - unit.get_width() // 2, cy + 50))

        label = self.font_tiny.render("SPEED", True, GRAY_MED)
        surface.blit(label, (cx - label.get_width() // 2, cy - radius - 18))

    def _draw_tachometer(self, surface, cx, cy, radius, car):
        """Desenha o conta-giros (tacômetro) com redline"""
        pygame.draw.circle(surface, GAUGE_BG, (cx, cy), radius)
        pygame.draw.circle(surface, GAUGE_RING, (cx, cy), radius, 3)

        # Desenha faixa pontilhada vermelha para o redline
        redline_start = -225 + (RPM_REDLINE / RPM_MAX) * 270
        for a in range(int(redline_start), 46, 2):
            angle = math.radians(a)
            x = cx + math.cos(angle) * (radius - 3)
            y = cy + math.sin(angle) * (radius - 3)
            pygame.draw.circle(surface, NEON_RED, (int(x), int(y)), 2)

        # Marcações principais de rotação (0 a 8 mil RPM)
        for i in range(0, 9):
            angle = math.radians(-225 + i * (270 / 8))
            inner = radius - 12
            outer = radius - 4
            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner
            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer
            color = NEON_RED if (i * 1000) >= RPM_REDLINE else WHITE
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)

        # Agulha do RPM
        rpm_frac = min(1.0, car.rpm / RPM_MAX)
        needle_angle = math.radians(-225 + rpm_frac * 270)
        needle_len = radius - 18
        nx = cx + math.cos(needle_angle) * needle_len
        ny = cy + math.sin(needle_angle) * needle_len
        needle_color = NEON_RED if car.is_at_redline else NEON_ORANGE
        pygame.draw.line(surface, needle_color, (cx, cy), (nx, ny), 3)
        pygame.draw.circle(surface, WHITE, (cx, cy), 5)

        # Luz indicadora de mudança (Shift Light) - pisca quando o motor corta
        if car.is_at_redline:
            blink = (int(self._anim_timer * 8) % 2 == 0)
            if blink:
                pygame.draw.circle(surface, NEON_RED, (cx, cy - radius - 14), 8)
                glow_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*NEON_RED, 60), (12, 12), 12)
                surface.blit(glow_surf, (cx - 12, cy - radius - 26))
        else:
            pygame.draw.circle(surface, GRAY_DARK, (cx, cy - radius - 14), 8)
            pygame.draw.circle(surface, GAUGE_RING, (cx, cy - radius - 14), 8, 1)

        # Texto do RPM
        rpm_text = self.font_medium.render(f"{int(car.rpm)}", True, WHITE)
        surface.blit(rpm_text, (cx - rpm_text.get_width() // 2, cy + 25))
        unit = self.font_tiny.render("RPM", True, GRAY_MED)
        surface.blit(unit, (cx - unit.get_width() // 2, cy + 50))

        label = self.font_tiny.render("TACH", True, GRAY_MED)
        surface.blit(label, (cx - label.get_width() // 2, cy - radius - 18))

        # Alerta visual de motor em risco caso esteja sobreaquecendo
        if car.redline_progress > 0.1:
            bar_w = radius * 2
            bar_h = 6
            bar_x = cx - radius
            bar_y = cy + 68

            pygame.draw.rect(surface, GRAY_DARK, (bar_x, bar_y, bar_w, bar_h))

            fill_w = int(bar_w * car.redline_progress)
            danger_color = NEON_RED if int(self._anim_timer * 6) % 2 == 0 else NEON_ORANGE

            pygame.draw.rect(surface, danger_color, (bar_x, bar_y, fill_w, bar_h))
            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1)
            warn = self.font_tiny.render("ENGINE DANGER!", True, danger_color)
            surface.blit(warn, (cx - warn.get_width() // 2, bar_y + 8))

    def _draw_gear_indicator(self, surface, x, y, car, shifter):
        """Desenha a moldura com a marcha atual em texto gigante."""
        w, h = 100, 120
        gear = car.current_gear
        gear_color = GEAR_COLORS.get(gear, GRAY_MED)

        pygame.draw.rect(surface, GAUGE_BG, (x, y, w, h))

        # Se houver erro de embreagem/marcha arranhada recente, pisca em vermelho
        border_color = gear_color
        if shifter.has_error:
            border_color = NEON_RED if int(self._anim_timer * 10) % 2 == 0 else GAUGE_BG
        pygame.draw.rect(surface, border_color, (x, y, w, h), 3)

        # Mapeia números de marchas para texto
        gear_labels = {
            GEAR_NEUTRAL: "N",
            GEAR_FIRST: "1",
            GEAR_SECOND: "2",
            GEAR_THIRD: "3",
            GEAR_FOURTH: "4",
            GEAR_FIFTH: "5",
            GEAR_SIXTH: "6",
            GEAR_REVERSE: "R",
        }
        gear_str = gear_labels.get(gear, "?")

        # Se o motor explodiu, desenha um "X" em vermelho
        if car.engine_blown:
            gear_str = "X"
            gear_color = NEON_RED

        gear_render = self.font_gear.render(gear_str, True, gear_color)
        surface.blit(gear_render, (x + w // 2 - gear_render.get_width() // 2, y + 15))

        label = self.font_small.render("GEAR", True, GRAY_MED)
        surface.blit(label, (x + w // 2 - label.get_width() // 2, y + h - 28))

        if car.engine_blown:
            status = self.font_tiny.render("BLOWN!", True, NEON_RED)
            surface.blit(status, (x + w // 2 - status.get_width() // 2, y + h + 5))

    def _draw_h_pattern_display(self, surface, x, y, shifter):
        """
        Desenha a moldura do H-Pattern contendo o desenho das canaletas,
        a posição atual do knob e a linha de trajetória iluminada até a próxima marcha
        """
        w, h = 210, 180
        pygame.draw.rect(surface, GAUGE_BG, (x, y, w, h))
        pygame.draw.rect(surface, GAUGE_RING, (x, y, w, h), 2)

        label = self.font_small.render("H-PATTERN", True, NEON_CYAN)
        surface.blit(label, (x + w // 2 - label.get_width() // 2, y + 4))

        hx = x + w // 2
        hy = y + h // 2 + 10
        spacing_x = 25
        spacing_y = 30

        # === Desenha a grade (metal do portão de marchas) ===
        gate_color = GRAY_DARK
        lw = 2

        # Barra horizontal Neutra (R até 5/6)
        pygame.draw.line(surface, gate_color, (hx - 3 * spacing_x, hy), (hx + 3 * spacing_x, hy), lw)
        # Barra da Ré
        pygame.draw.line(surface, gate_color, (hx - 3 * spacing_x, hy), (hx - 3 * spacing_x, hy - spacing_y), lw)
        # Barra de 1ª/2ª
        pygame.draw.line(surface, gate_color, (hx - 1 * spacing_x, hy - spacing_y), (hx - 1 * spacing_x, hy + spacing_y), lw)
        # Barra de 3ª/4ª
        pygame.draw.line(surface, gate_color, (hx + 1 * spacing_x, hy - spacing_y), (hx + 1 * spacing_x, hy + spacing_y), lw)
        # Barra de 5ª/6ª
        pygame.draw.line(surface, gate_color, (hx + 3 * spacing_x, hy - spacing_y), (hx + 3 * spacing_x, hy + spacing_y), lw)

        # === Desenha o caminho luminoso para a próxima marcha recomendada ===
        current_gear = shifter.current_gear
        next_gear, hint_text = shifter.get_next_gear_hint()

        if next_gear is not None:
            # Pega o caminho calculado
            path_positions = shifter.get_path_to_next_gear()
            if path_positions:
                pixel_points = []
                for pt in path_positions:
                    pixel_points.append((hx + pt[0] * spacing_x, hy + pt[1] * spacing_y))

                path_color = (*NEON_GREEN[:3],)

                # Liga os pontos com uma linha verde iluminada
                for i in range(len(pixel_points) - 1):
                    p1 = pixel_points[i]
                    p2 = pixel_points[i + 1]
                    pygame.draw.line(surface, path_color, p1, p2, 3)

                    # Desenha pequenas setas direcionais no meio do caminho
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    length = math.sqrt(dx * dx + dy * dy)
                    if length > 0:
                        mid_x = (p1[0] + p2[0]) / 2
                        mid_y = (p1[1] + p2[1]) / 2
                        ndx = dx / length * 5
                        ndy = dy / length * 5
                        arrow_pts = [
                            (mid_x + ndx, mid_y + ndy),
                            (mid_x - ndy * 0.5, mid_y + ndx * 0.5),
                            (mid_x + ndy * 0.5, mid_y - ndx * 0.5),
                        ]
                        pygame.draw.polygon(surface, path_color, [(int(ax), int(ay)) for ax, ay in arrow_pts])

        # === Desenha os números das marchas na tela ===
        gear_labels = {
            GEAR_REVERSE: "R",
            GEAR_FIRST:   "1",
            GEAR_SECOND:  "2",
            GEAR_THIRD:   "3",
            GEAR_FOURTH:  "4",
            GEAR_FIFTH:   "5",
            GEAR_SIXTH:   "6"
        }

        for gear, label_text in gear_labels.items():
            pos = H_PATTERN_POSITIONS[gear]
            gx = hx + pos[0] * spacing_x
            gy = hy + pos[1] * spacing_y

            # Colore o texto baseando se a marcha está engatada ou é a próxima recomendada
            if gear == current_gear:
                col = GEAR_COLORS[gear]
            elif gear == next_gear:
                pulse = 0.5 + 0.5 * math.sin(self._anim_timer * 4)
                col = tuple(int(c * pulse + 80 * (1 - pulse)) for c in NEON_GREEN[:3])
            else:
                col = GRAY_MED

            txt = self.font_tiny.render(label_text, True, col)
            surface.blit(txt, (gx - txt.get_width() // 2, gy - txt.get_height() // 2))

        # Desenha a letra "N" para representar Neutro no centro da crossbar (x=1, y=0)
        n_col = GEAR_COLORS[GEAR_NEUTRAL] if current_gear == GEAR_NEUTRAL else GRAY_DARK
        n_txt = self.font_tiny.render("N", True, n_col)
        nx = hx + 1 * spacing_x
        surface.blit(n_txt, (nx - n_txt.get_width() // 2, hy - n_txt.get_height() // 2))

        # === Desenha a esfera da alavanca (Knob) ===
        knob_pos = shifter.knob_position
        knob_x = hx + knob_pos[0] * spacing_x
        knob_y = hy + knob_pos[1] * spacing_y

        # Brilho de aura
        glow_surf = pygame.Surface((26, 26), pygame.SRCALPHA)
        gc = GEAR_COLORS[current_gear]
        pygame.draw.circle(glow_surf, (*gc, 50), (13, 13), 13)
        surface.blit(glow_surf, (knob_x - 13, knob_y - 13))

        # Alavanca propriamente dita (círculo sólido metálico)
        pygame.draw.circle(surface, gc, (knob_x, knob_y), 7)
        pygame.draw.circle(surface, WHITE, (knob_x, knob_y), 7, 2)

        # Legenda das teclas na base da caixa H
        if hint_text and next_gear is not None:
            hint_label = self.font_tiny.render(f"Next: {hint_text}", True, NEON_GREEN)
            surface.blit(
                hint_label,
                (x + w // 2 - hint_label.get_width() // 2, y + h - 20)
            )
        elif next_gear is None and current_gear == GEAR_SIXTH:
            max_label = self.font_tiny.render("MAX GEAR", True, NEON_YELLOW)
            surface.blit(
                max_label,
                (x + w // 2 - max_label.get_width() // 2, y + h - 20)
            )
        elif next_gear is None and current_gear == GEAR_REVERSE:
            rev_label = self.font_tiny.render("REVERSE", True, GEAR_COLORS[GEAR_REVERSE])
            surface.blit(
                rev_label,
                (x + w // 2 - rev_label.get_width() // 2, y + h - 20)
            )

    def _draw_pedals(self, surface, x, y, car):
        """Desenha os dois pedais que afundam na tela (Acelerador e Embreagem)"""
        pedal_w = 55
        pedal_h = 100
        gap = 20

        # === 1. Acelerador (GAS - Tecla W) ===
        gas_x = x
        gas_pressed = car.gas_pressed

        # Desenha a moldura de ferro do pedal
        pygame.draw.rect(
            surface,
            GRAY_DARK,
            (gas_x, y, pedal_w, pedal_h + 20)
        )
        pygame.draw.rect(
            surface,
            GAUGE_RING,
            (gas_x, y, pedal_w, pedal_h + 20),
            2
        )

        # Desenha o pedal afundado proporcionalmente
        depress = 30 if gas_pressed else 0
        pedal_color = PEDAL_GAS_ACTIVE if gas_pressed else PEDAL_IDLE
        pygame.draw.rect(
            surface,
            pedal_color,
            (gas_x + 5, y + 5 + depress, pedal_w - 10, pedal_h - depress)
        )

        if gas_pressed:
            glow = pygame.Surface(
                (pedal_w - 10, pedal_h - depress),
                pygame.SRCALPHA
            )
            glow.fill((*PEDAL_GAS_ACTIVE, 40))
            surface.blit(glow, (gas_x + 5, y + 5 + depress))

        # Texto indicador
        key_label = self.font_medium.render("W", True, WHITE)
        surface.blit(
            key_label,
            (gas_x + pedal_w // 2 - key_label.get_width() // 2, y + pedal_h + 25)
        )
        desc = self.font_tiny.render("GAS", True, GRAY_MED)
        surface.blit(
            desc,
            (gas_x + pedal_w // 2 - desc.get_width() // 2, y + pedal_h + 50)
        )

        # === 2. Embreagem (CLUTCH - Tecla ESPAÇO) ===
        clutch_x = x + pedal_w + gap
        clutch_pressed = car.clutch_pressed

        # Moldura de ferro
        pygame.draw.rect(surface, GRAY_DARK, (clutch_x, y, pedal_w, pedal_h + 20))
        pygame.draw.rect(surface, GAUGE_RING, (clutch_x, y, pedal_w, pedal_h + 20), 2)

        # Pedal afundado
        depress_c = 30 if clutch_pressed else 0
        pedal_color_c = PEDAL_CLUTCH_ACTIVE if clutch_pressed else PEDAL_IDLE
        pygame.draw.rect(
            surface, pedal_color_c,
            (clutch_x + 5, y + 5 + depress_c, pedal_w - 10, pedal_h - depress_c)
        )

        if clutch_pressed:
            glow = pygame.Surface(
                (pedal_w - 10, pedal_h - depress_c),
                pygame.SRCALPHA
            )
            glow.fill((*PEDAL_CLUTCH_ACTIVE, 40))
            surface.blit(
                glow,
                (clutch_x + 5, y + 5 + depress_c)
            )

        # Texto indicador
        key_label2 = self.font_small.render("SPC", True, WHITE)
        surface.blit(
            key_label2,
            (clutch_x + pedal_w // 2 - key_label2.get_width() // 2, y + pedal_h + 27)
        )
        desc2 = self.font_tiny.render("CLUTCH", True, GRAY_MED)
        surface.blit(
            desc2,
            (clutch_x + pedal_w // 2 - desc2.get_width() // 2, y + pedal_h + 50)
        )

    def _draw_shift_hints(self, surface, x, y, shifter):
        """Desenha a caixa de dicas com as setas pendentes ou o aviso de arranhada de câmbio"""
        # Se o jogador iniciou o Neutro (barra central), mostra a coordenada do knob
        pending = shifter.get_pending_sequence()
        if pending:
            seq_str = " -> ".join(pending)

            seq_label = self.font_tiny.render("Input:", True, GRAY_MED)
            surface.blit(seq_label, (x, y))

            seq_text = self.font_small.render(seq_str, True, NEON_YELLOW)
            surface.blit(seq_text, (x, y + 18))

        # Se houver erro ativo, avisa "GRIND!" piscando na tela
        if shifter.has_error:
            err_text = self.font_small.render("GRIND!", True, NEON_RED)
            surface.blit(err_text, (x, y + 50))

        # Texto fixo instrutivo
        hint = self.font_tiny.render("Hold SPACE + Arrows", True, GRAY_DARK)
        surface.blit(hint, (x, y + 85))
        hint2 = self.font_tiny.render("to shift gears", True, GRAY_DARK)
        surface.blit(hint2, (x, y + 102))
