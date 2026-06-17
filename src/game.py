"""
Módulo coordenador principal do jogo.
Implementa a classe Game que gerencia o loop do jogo, as transições de tela e os inputs.
"""

import pygame
import sys
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    DARK_BG, RPM_MAX,
    STATE_MAIN_MENU, STATE_CAR_SELECT, STATE_STAGE_SELECT, STATE_COUNTDOWN, STATE_RACING, STATE_WIN, STATE_LOSE,
    CAR_BALANCED, CAR_HIGH_ACCEL, CAR_TOP_SPEED, CAR_CONFIGS, STAGE_CONFIGS,
    GEAR_NEUTRAL
)
from src.sound_manager import SoundManager
from src.sprite_generator import SpriteGenerator
from src.shifter import Shifter
from src.car import Car
from src.ai_driver import AIDriver
from src.dashboard import Dashboard
from src.race import Race
from src.menu import MainMenu, CarSelectMenu, StageSelectMenu

class Game:
    """
    Classe central do jogo.
    Coordena as telas de menu, a corrida, o processamento de eventos do Pygame,
    o gerenciamento de tempo (delta time) e a renderização geral.
    """

    def __init__(self):
        """Inicializa a janela e os subsistemas do jogo."""
        # Configuração da janela do Pygame
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("LateShift - Drag Racing")
        self.clock = pygame.time.Clock()

        # Instancia gerenciador de áudio e gerador de sprites
        self.sound_manager = SoundManager()
        self.sprite_generator = SpriteGenerator()

        # Instancia as telas de menu
        self.main_menu = MainMenu()
        self.car_select_menu = CarSelectMenu(self.sprite_generator)
        self.stage_select_menu = StageSelectMenu()

        # Instancia componentes da corrida
        self.dashboard = Dashboard()
        self.race_track = Race()
        self.shifter = Shifter(self.sound_manager)

        # Estado inicial do jogo (Menu Principal)
        self.state = STATE_MAIN_MENU

        # Dados da seleção do jogador
        self.selected_car_index = 0
        self.selected_car_type = CAR_BALANCED
        self.selected_stage_index = 0

        # Carros (serão instanciados ao iniciar a corrida)
        self.player_car = None
        self.ai_driver = None

        # Variáveis da contagem regressiva da largada
        self.countdown_value = 3
        self.countdown_timer = 0.0

    def run(self):
        """Loop principal do jogo (game loop)."""
        running = True

        while running:
            # Calcula o delta time em segundos (fator de correção de FPS)
            dt = self.clock.tick(FPS) / 1000.0

            # 1. Captura e processa eventos do Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                self._handle_event(event)

            # 2. Atualiza a lógica do jogo dependendo do estado atual
            keys = pygame.key.get_pressed()
            self._update(dt, keys)

            # 3. Renderiza o frame na tela
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # === PROCESSAMENTO DE EVENTOS ===

    def _handle_event(self, event):
        """Distribui o processamento dos eventos teclado/mouse com base no estado atual."""
        if event.type != pygame.KEYDOWN:
            return

        # Controle de volume geral (Page Up para aumentar, Page Down para diminuir)
        if event.key == pygame.K_PAGEUP:
            new_vol = min(1.0, self.sound_manager.volume + 0.1)
            self.sound_manager.set_volume(new_vol)
            print(f"[SoundManager] Volume geral: {int(new_vol * 100)}%")
        elif event.key == pygame.K_PAGEDOWN:
            new_vol = max(0.0, self.sound_manager.volume - 0.1)
            self.sound_manager.set_volume(new_vol)
            print(f"[SoundManager] Volume geral: {int(new_vol * 100)}%")

        if self.state == STATE_MAIN_MENU:
            self._handle_main_menu_event(event)
        elif self.state == STATE_CAR_SELECT:
            self._handle_car_select_event(event)
        elif self.state == STATE_STAGE_SELECT:
            self._handle_stage_select_event(event)
        elif self.state == STATE_COUNTDOWN:
            self._handle_countdown_event(event)
        elif self.state == STATE_RACING:
            self._handle_racing_event(event)
        elif self.state in (STATE_WIN, STATE_LOSE):
            self._handle_result_event(event)

    def _handle_main_menu_event(self, event):
        """Lida com as opções numéricas no Menu Principal."""
        if event.key == pygame.K_1:
            self.state = STATE_STAGE_SELECT
        elif event.key == pygame.K_2:
            self.state = STATE_CAR_SELECT
        elif event.key == pygame.K_3:
            pygame.quit()
            sys.exit()

    def _handle_car_select_event(self, event):
        """Lida com as teclas de seleção de carro."""
        car_types = [CAR_BALANCED, CAR_HIGH_ACCEL, CAR_TOP_SPEED]
        if event.key == pygame.K_1:
            self.selected_car_index = 0
            self.selected_car_type = car_types[0]
            self.state = STATE_MAIN_MENU
        elif event.key == pygame.K_2:
            self.selected_car_index = 1
            self.selected_car_type = car_types[1]
            self.state = STATE_MAIN_MENU
        elif event.key == pygame.K_3:
            self.selected_car_index = 2
            self.selected_car_type = car_types[2]
            self.state = STATE_MAIN_MENU
        elif event.key == pygame.K_ESCAPE:
            self.state = STATE_MAIN_MENU

    def _handle_stage_select_event(self, event):
        """Lida com as teclas de seleção de fase e inicia a corrida."""
        if pygame.K_1 <= event.key <= pygame.K_6:
            self.selected_stage_index = event.key - pygame.K_1
            self._start_race()
        elif event.key == pygame.K_ESCAPE:
            self.state = STATE_MAIN_MENU

    def _handle_countdown_event(self, event):
        """Permite que o jogador controle a embreagem e coloque a 1ª marcha antes da largada."""
        if self.player_car:
            keys = pygame.key.get_pressed()
            clutch = keys[pygame.K_SPACE]
            gear_changed, error = self.shifter.handle_event(event, clutch)
            if error:
                self.player_car.apply_grind_penalty()
            self.player_car.current_gear = self.shifter.current_gear

    def _handle_racing_event(self, event):
        """Trata as trocas de marchas feitas pelo jogador usando o H-Pattern na corrida."""
        if self.player_car:
            keys = pygame.key.get_pressed()
            clutch = keys[pygame.K_SPACE]
            gear_changed, error = self.shifter.handle_event(event, clutch)
            if error:
                self.player_car.apply_grind_penalty()
            self.player_car.current_gear = self.shifter.current_gear

    def _handle_result_event(self, event):
        """Volta para o menu principal ao apertar qualquer tecla de ação após o término."""
        if event.key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_RETURN):
            self.state = STATE_MAIN_MENU

    # === ATUALIZAÇÃO DA LÓGICA (UPDATE) ===

    def _update(self, dt, keys):
        """Escolhe qual update rodar dependendo do estado atual."""
        if self.state == STATE_MAIN_MENU:
            self.sound_manager.stop_engine_sound()
            self.main_menu.update(dt)
        elif self.state == STATE_CAR_SELECT:
            self.sound_manager.stop_engine_sound()
            self.car_select_menu.update(dt)
        elif self.state == STATE_STAGE_SELECT:
            self.sound_manager.stop_engine_sound()
            self.stage_select_menu.update(dt)
        elif self.state == STATE_COUNTDOWN:
            self._update_countdown(dt, keys)
        elif self.state == STATE_RACING:
            self._update_racing(dt, keys)
        elif self.state in (STATE_WIN, STATE_LOSE):
            self.sound_manager.stop_engine_sound()

    def _update_countdown(self, dt, keys):
        """Atualiza a contagem regressiva e permite que o motor seja acelerado."""
        if self.player_car:
            self.player_car.gas_pressed = keys[pygame.K_w]
            self.player_car.clutch_pressed = keys[pygame.K_SPACE]
            self.player_car.current_gear = self.shifter.current_gear
            # Atualiza o som de rotação do motor por marcha
            self.sound_manager.update_engine_sound(self.player_car.current_gear, self.player_car.clutch_pressed)
            # Apenas rotaciona o motor (RPM), sem mover o carro física lateralmente
            self._update_rpm_only(dt)

        self.shifter.update(dt)
        self.dashboard.update(dt)

        # Atualiza cronômetro de 3, 2, 1...
        self.countdown_timer += dt
        if self.countdown_timer >= 1.0:
            self.countdown_timer = 0.0
            if self.countdown_value > 0:
                self.sound_manager.play("countdown_beep")
                self.countdown_value -= 1
            else:
                # Inicia a corrida ao bater o zero (GO!)
                self.sound_manager.play("countdown_go")
                self.state = STATE_RACING
                if self.ai_driver:
                    self.ai_driver.start_race()

    def _update_rpm_only(self, dt):
        """Aumenta/reduz apenas o RPM na largada, com risco de explodir o motor."""
        car = self.player_car
        if car.gas_pressed:
            if car.clutch_pressed or car.current_gear == GEAR_NEUTRAL:
                car.rpm += 5000 * dt
            else:
                car.rpm += 1500 * dt
        else:
            car.rpm -= 3500 * dt

        car.rpm = max(0.0, min(car.rpm, RPM_MAX))

        # Motor quebra se cortar giro antes da hora
        car._check_engine_explosion(dt)
        if car.engine_blown:
            self.sound_manager.play("explosion")
            self.state = STATE_LOSE

    def _update_racing(self, dt, keys):
        """Atualiza a simulação física da corrida e as posições de chegada."""
        # Captura pedal do jogador
        self.player_car.gas_pressed = keys[pygame.K_w]
        self.player_car.clutch_pressed = keys[pygame.K_SPACE]
        self.player_car.current_gear = self.shifter.current_gear

        # Atualiza som de rotação do motor
        self.sound_manager.update_engine_sound(self.player_car.current_gear, self.player_car.clutch_pressed)

        # Atualiza jogador e IA
        self.player_car.update(dt)
        self.ai_driver.update(dt)

        # Atualiza os subsistemas
        self.shifter.update(dt)
        self.dashboard.update(dt)
        self.race_track.update(dt, self.player_car.speed, self.ai_driver.car.speed)

        # Atualiza a rotação das rodas dos sprites
        player_sprite = self.sprite_generator.get_sprite(self.selected_car_type)
        if player_sprite:
            player_sprite.update(dt, self.player_car.speed)

        stage = STAGE_CONFIGS[self.selected_stage_index]
        ai_sprite = self.sprite_generator.get_sprite(stage["ai_car_type"])
        if ai_sprite:
            ai_sprite.update(dt, self.ai_driver.car.speed)

        # Fim de jogo caso o motor do jogador exploda
        if self.player_car.engine_blown:
            self.sound_manager.play("explosion")
            self.state = STATE_LOSE
            return

        # Verifica vitória ou derrota pela linha de chegada
        stage_distance = stage["distance"]
        if self.player_car.distance >= stage_distance:
            self.state = STATE_WIN
            self.sound_manager.play("win")
        elif self.ai_driver.car.distance >= stage_distance:
            self.state = STATE_LOSE
            self.sound_manager.play("lose")

    # === RENDERIZAÇÃO (DRAW) ===

    def _draw(self):
        """Desenha a tela de acordo com o estado do jogo."""
        if self.state == STATE_MAIN_MENU:
            self.main_menu.draw(self.screen)
        elif self.state == STATE_CAR_SELECT:
            self.car_select_menu.draw(self.screen, self.selected_index_car())
        elif self.state == STATE_STAGE_SELECT:
            self.stage_select_menu.draw(self.screen)
        elif self.state == STATE_COUNTDOWN:
            self._draw_race_scene()
            self.race_track.draw_countdown(self.screen, self.countdown_value)
        elif self.state == STATE_RACING:
            self._draw_race_scene()
        elif self.state == STATE_WIN:
            self._draw_race_scene()
            self.race_track.draw_result(self.screen, won=True)
        elif self.state == STATE_LOSE:
            self._draw_race_scene()
            self.race_track.draw_result(self.screen, won=False, engine_blown=self.player_car.engine_blown if self.player_car else False)

    def selected_index_car(self):
        """Auxiliar didático para retornar o índice do carro selecionado."""
        return self.selected_car_index

    def _draw_race_scene(self):
        """Renderiza o cenário da corrida, carros e o painel de instrumentos."""
        self.screen.fill(DARK_BG)

        # Puxa o sprite dinâmico do carro do jogador e IA (o oponente usa o carro da fase)
        player_sprite = self.sprite_generator.get_sprite(self.selected_car_type)
        stage = STAGE_CONFIGS[self.selected_stage_index]
        ai_sprite = self.sprite_generator.get_sprite(stage["ai_car_type"])

        # Desenha a pista de corrida com os competidores
        ai_car = self.ai_driver.car if self.ai_driver else None
        self.race_track.draw_track(self.screen, self.player_car, ai_car, player_sprite, ai_sprite)

        # Desenha o painel de instrumentos por cima
        self.dashboard.draw(self.screen, self.player_car, self.shifter)

    # === CONTROLE DE CORRIDA ===

    def _start_race(self):
        """Prepara todos os dados e reseta componentes para uma nova largada."""
        # Cria o carro do jogador
        config = CAR_CONFIGS[self.selected_car_type]
        self.player_car = Car(config)

        # Cria o oponente da IA com a dificuldade e o carro configurado para a fase
        stage = STAGE_CONFIGS[self.selected_stage_index]
        ai_config = CAR_CONFIGS[stage["ai_car_type"]]
        self.ai_driver = AIDriver(ai_config, stage["ai_multiplier"])

        # Reseta o câmbio manual e o cenário
        self.shifter.reset()
        self.race_track.set_stage(self.selected_stage_index)

        # Prepara a contagem regressiva
        self.state = STATE_COUNTDOWN
        self.countdown_value = 3
        self.countdown_timer = 0.0

        # Toca som de bipe inicial da largada
        self.sound_manager.play("countdown_beep")
