"""
Módulo do piloto controlado por Inteligência Artificial (oponente)
Implementa o comportamento da IA para acelerar e trocar marchas automaticamente
"""

import random
from src.constants import (
    GEAR_NEUTRAL, GEAR_FIRST, GEAR_SECOND,
    GEAR_THIRD, GEAR_FOURTH, GEAR_FIFTH, GEAR_SIXTH
)
from src.car import Car

class AIDriver:
    """
    Controla o carro do oponente de forma automatizada
    Troca marchas sequencialmente com base em um RPM ideal e acelera continuamente
    """

    def __init__(self, car_config, ai_multiplier=1.0):
        """
        Inicializa o oponente da IA ajustando sua dificuldade
        :param car_config: Dicionário com atributos do carro base
        :param ai_multiplier: Multiplicador para deixar a IA mais rapida/lenta
        """
        # Copia a configuracao para nao alterar a do jogador
        self.config = car_config.copy()
        
        # Ajusta velocidade e aceleracao da IA conforme a dificuldade do estagio
        self.config["acceleration"] = car_config["acceleration"] * ai_multiplier
        self.config["top_speed"] = car_config["top_speed"] * ai_multiplier

        # Cria a instância do carro controlado pela IA
        self.car = Car(self.config)

        # Configurações de comportamento aleatórias para simular um piloto humano
        self.shift_rpm = 5600 + random.randint(-200, 200)  # Ponto de rotação ideal para trocar
        self.reaction_delay = random.uniform(0.1, 0.3)      # Tempo de reação na largada (segundos)
        self.reaction_timer = 0.0
        self.race_started = False

    def reset(self):
        """Reseta o estado da IA para a largada"""
        self.car.reset()
        self.reaction_timer = 0.0
        self.race_started = False
        self.shift_rpm = 5600 + random.randint(-200, 200)
        self.reaction_delay = random.uniform(0.1, 0.3)

    def start_race(self):
        """Sinaliza que a corrida foi iniciada e prepara a largada da IA"""
        self.race_started = True
        self.reaction_timer = 0.0
        # A IA larga engatada na 1ª marcha com motor cheio (giro alto) para resposta imediata
        self.car.current_gear = GEAR_FIRST
        self.car.rpm = 4500.0

    def update(self, dt):
        """
        Atualiza as ações da IA a cada frame
        :param dt: Tempo delta em segundos
        """
        if not self.race_started:
            return

        # Simula o tempo de reação antes da IA começar a acelerar
        self.reaction_timer += dt
        if self.reaction_timer < self.reaction_delay:
            return

        # IA sempre pisa fundo no acelerador e mantém embreagem solta
        self.car.gas_pressed = True
        self.car.clutch_pressed = False

        # Verifica se precisa subir a marcha
        self._auto_shift()

        # Atualiza a física do carro da IA
        self.car.update(dt)

    def _auto_shift(self):
        """
        Troca as marchas da IA de forma automática baseada no RPM do motor e limite de velocidade da marcha
        As reduções e perdas por atrito de embreagem são simuladas de forma simples
        """
        current = self.car.current_gear
        rpm = self.car.rpm

        # Importa limite de velocidade das marchas para evitar travamento em giros baixos da física
        from src.constants import GEAR_SPEED_LIMITS

        max_speed_gear = self.car.top_speed * GEAR_SPEED_LIMITS.get(current, 1.0)
        # Se o RPM passar do ponto de troca OU a velocidade estiver muito próxima do limite físico da marcha, a IA sobe a marcha
        should_shift = (rpm > self.shift_rpm) or (current != GEAR_NEUTRAL and self.car.speed >= max_speed_gear * 0.92)

        # Trocas de marcha sequenciais da IA
        if current == GEAR_NEUTRAL and rpm > 1000:
            self.car.current_gear = GEAR_FIRST
        elif current == GEAR_FIRST and should_shift:
            self.car.current_gear = GEAR_SECOND
            self.car.rpm *= 0.667  # Simula queda de giro de 1 para 2
        elif current == GEAR_SECOND and should_shift:
            self.car.current_gear = GEAR_THIRD
            self.car.rpm *= 0.717  # Simula queda de giro para 3
        elif current == GEAR_THIRD and should_shift:
            self.car.current_gear = GEAR_FOURTH
            self.car.rpm *= 0.750  # Simula queda de giro para 4
        elif current == GEAR_FOURTH and should_shift:
            self.car.current_gear = GEAR_FIFTH
            self.car.rpm *= 0.783  # Simula queda de giro para 5
        elif current == GEAR_FIFTH and should_shift:
            self.car.current_gear = GEAR_SIXTH
            self.car.rpm *= 0.817  # Simula queda de giro para 6

