"""
Módulo do câmbio H-Pattern
Implementa o Shifter que gerencia a posição física da alavanca (knob) e a marcha engatada
"""

import pygame
from src.constants import (
    GEAR_NEUTRAL, KNOB_ADJACENCY, KNOB_GEAR_MAP, NEXT_GEAR_HINTS, H_PATTERN_POSITIONS
)

class Shifter:
    """
    Controla o câmbio manual H-Pattern
    A alavanca (knob) se move pela grade física usando as setas do teclado
    Para mover a alavanca, o jogador precisa segurar a embreagem (SPACE)
    """

    def __init__(self, sound_manager=None):
        """
        Inicializa o shifter na posição Neutro central (1, 0)
        :param sound_manager: Gerenciador de som do jogo
        """
        self.sound_manager = sound_manager
        
        # Marcha atual engatada
        self.current_gear = GEAR_NEUTRAL

        # Posição x, y atual do knob na grade do H-pattern
        self.knob_position = (1, 0)  # Posição central (Neutro entre 3ª e 4ª)

        # Última marcha engatada válida (usado para exibir dicas de navegação)
        self._last_engaged_gear = GEAR_NEUTRAL

        # Flags de controle visual/sonoro de troca
        self.last_shift_success = False
        self.last_shift_error = False
        self._error_timer = 0.0

        # Mapeamento simples de teclas direcionais para strings de movimento
        self._arrow_keys = {
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
        }

    def reset(self):
        """Reseta o câmbio para a posição inicial Neutro"""
        self.current_gear = GEAR_NEUTRAL
        self.knob_position = (1, 0)
        self._last_engaged_gear = GEAR_NEUTRAL
        self.last_shift_success = False
        self.last_shift_error = False
        self._error_timer = 0.0

    def handle_event(self, event, clutch_pressed):
        """
        Trata o pressionamento de teclas direcionais para mover a alavanca
        Retorna se a marcha mudou ou se houve um erro
        :param event: Evento do Pygame
        :param clutch_pressed: Indica se o pedal de embreagem está pressionado
        :return: Tupla (gear_changed: bool, error: bool)
        """
        if event.type != pygame.KEYDOWN:
            return False, False

        # Se não for uma das setas do teclado, ignora
        if event.key not in self._arrow_keys:
            return False, False

        direction = self._arrow_keys[event.key]

        # REGRA PRINCIPAL: Sem embreagem pressionada, o câmbio trava e arranha (gear grind)
        if not clutch_pressed:
            self._trigger_grind_error()
            return False, True

        # Verifica se o movimento na direção desejada é permitido a partir da posição atual
        valid_moves = KNOB_ADJACENCY.get(self.knob_position, {})
        if direction not in valid_moves:
            # Movimento contra as paredes do câmbio: ignora sem gerar erro
            return False, False

        # Move o knob para a nova coordenada
        new_pos = valid_moves[direction]
        self.knob_position = new_pos

        # Determina a marcha correspondente à nova coordenada do knob
        old_gear = self.current_gear
        new_gear = KNOB_GEAR_MAP.get(new_pos, GEAR_NEUTRAL)
        self.current_gear = new_gear

        # Se engatou uma marcha de fato (saiu do neutro/barra horizontal)
        if new_gear != GEAR_NEUTRAL:
            self._last_engaged_gear = new_gear

            if new_gear != old_gear:
                self.last_shift_success = True
                # Toca o som de clique de engate
                if self.sound_manager:
                    self.sound_manager.play("gear_shift")
                return True, False

        return False, False

    def update(self, dt):
        """Atualiza timers do shifter"""
        # Diminui o tempo de exibição do alerta de erro
        if self._error_timer > 0:
            self._error_timer -= dt
            if self._error_timer <= 0:
                self.last_shift_error = False

    def get_next_gear_hint(self):
        """
        Informa qual é a próxima marcha sugerida e a sequência de setas para ela
        :return: Tupla (proxima_marcha: int ou None, texto_dica: str)
        """
        # Se estiver em uma marcha engatada, recomenda a próxima
        if self.current_gear != GEAR_NEUTRAL:
            return NEXT_GEAR_HINTS.get(self.current_gear, (None, ""))

        # Se estiver no neutro, recomenda a próxima baseada na última marcha engatada
        if self._last_engaged_gear != GEAR_NEUTRAL:
            return NEXT_GEAR_HINTS.get(self._last_engaged_gear, (None, ""))

        # Do contrário, sugere a 1ª marcha por padrão
        return NEXT_GEAR_HINTS.get(GEAR_NEUTRAL, (None, ""))

    def get_path_to_next_gear(self):
        """
        Encontra o caminho do knob atual até o slot da próxima marcha
        Utiliza busca em largura (BFS) didática
        """
        next_gear, _ = self.get_next_gear_hint()
        if next_gear is None:
            return []

        target_pos = H_PATTERN_POSITIONS.get(next_gear)
        if target_pos is None or target_pos == self.knob_position:
            return []

        return self._bfs_path(self.knob_position, target_pos)

    def get_pending_sequence(self):
        """Retorna uma string simples representando a posição do knob quando em neutro"""
        if self.current_gear == GEAR_NEUTRAL:
            x, y = self.knob_position
            return [f"({x},{y})"]
        return []

    @property
    def has_error(self):
        """Informa se ocorreu um erro de marcha recentemente"""
        return self._error_timer > 0

    def _trigger_grind_error(self):
        """
        Ativa a penalidade de erro (arranhada de marcha)
        Mantém o knob e a marcha atual na mesma posição, mas sinaliza o erro e emite o som
        """
        self.last_shift_error = True
        self.last_shift_success = False
        self._error_timer = 0.5  # Exibe erro por meio segundo

        if self.sound_manager:
            self.sound_manager.play("gear_grind")


    def _bfs_path(self, start, end):
        """
        Busca em largura simples para encontrar o caminho na grade
        Algoritmo clássico de faculdade (didático e legível)
        """
        if start == end:
            return [start]

        # Lista de tuplas (posição_atual, caminho_acumulado) agindo como fila (FIFO)
        queue = [(start, [start])]
        visited = {start}

        while len(queue) > 0:
            current, path = queue.pop(0)

            # Examina os vizinhos possíveis a partir do nó atual
            neighbors = KNOB_ADJACENCY.get(current, {})
            for direction, next_pos in neighbors.items():
                if next_pos == end:
                    return path + [next_pos]
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return []
