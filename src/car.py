"""
Módulo do carro do jogo.
Implementa a classe Car que simula a física do motor (RPM, velocidade, aceleração, motor explodido).
"""

from src.constants import (
    GEAR_NEUTRAL, GEAR_FIRST, GEAR_SECOND, GEAR_THIRD, GEAR_FOURTH,
    GEAR_FIFTH, GEAR_SIXTH, GEAR_REVERSE,
    GEAR_RATIOS, GEAR_SPEED_LIMITS,
    RPM_IDLE, RPM_REDLINE, RPM_MAX, RPM_EXPLODE_TIME
)

class Car:
    """
    Classe que representa o carro do jogador ou da IA.
    Contém a física básica de aceleração com base em marchas e RPM.
    """

    def __init__(self, config):
        """
        Inicializa o carro com suas configurações específicas.
        :param config: Dicionário com top_speed, acceleration, torque, etc.
        """
        self.config = config
        self.top_speed = config["top_speed"]
        self.acceleration_base = config["acceleration"]
        self.torque_mult = config["torque"]

        # Variáveis físicas e de estado
        self.speed = 0.0          # Velocidade atual em km/h
        self.distance = 0.0       # Distância total percorrida na pista
        self.rpm = 0.0            # Rotações Por Minuto do motor

        # Estado dos controles/pedais
        self.gas_pressed = False
        self.clutch_pressed = False

        # Marcha atual engatada (inicializa em Neutro)
        self.current_gear = GEAR_NEUTRAL

        # Estado de integridade do motor
        self.redline_timer = 0.0   # Tempo acumulado no limite de rotação (redline)
        self.engine_blown = False   # Indica se o motor explodiu

        # Posição X na tela de corrida
        self.screen_x = 100.0

    def reset(self):
        """Reseta o estado do carro para o início de uma nova corrida."""
        self.speed = 0.0
        self.distance = 0.0
        self.rpm = 0.0
        self.gas_pressed = False
        self.clutch_pressed = False
        self.current_gear = GEAR_NEUTRAL
        self.redline_timer = 0.0
        self.engine_blown = False
        self.screen_x = 100.0

    def update(self, dt):
        """
        Atualiza a física do carro a cada frame.
        :param dt: Tempo delta em segundos desde o último frame
        """
        if self.engine_blown:
            # Se o motor explodiu, o carro desacelera gradualmente e o RPM cai
            self.speed *= 0.96
            self.rpm = max(0, self.rpm - 3000 * dt)
            self.distance += self.speed * dt
            return

        # 1. Atualiza as rotações por minuto (RPM)
        self._update_rpm(dt)

        # 2. Verifica se o RPM ficou no limite de corte por muito tempo
        self._check_engine_explosion(dt)

        # 3. Atualiza a velocidade do carro
        self._update_speed(dt)

        # 4. Atualiza a distância percorrida
        self.distance += self.speed * dt

    def _update_rpm(self, dt):
        """Atualiza o RPM baseado na aceleração, embreagem e marcha."""
        if self.gas_pressed:
            if self.clutch_pressed or self.current_gear == GEAR_NEUTRAL:
                # Com a embreagem pisada ou em ponto morto, o motor sobe giro livremente
                self.rpm += 5000 * dt
            else:
                # Engatado e acelerando: o RPM sobe dependendo do torque da marcha
                # Marchas mais altas aceleram o motor mais devagar (relação física)
                gear_rpm_mult = {
                    GEAR_FIRST: 1.0,
                    GEAR_SECOND: 0.85,
                    GEAR_THIRD: 0.72,
                    GEAR_FOURTH: 0.60,
                    GEAR_FIFTH: 0.50,
                    GEAR_SIXTH: 0.40,
                    GEAR_REVERSE: 0.9,
                }.get(self.current_gear, 1.0)

                load_factor = self.speed / max(1.0, self.top_speed)
                self.rpm += 3000 * dt * (1.0 - load_factor * 0.75) * gear_rpm_mult
        else:
            # Soltou o acelerador: o RPM decai
            if self.clutch_pressed or self.current_gear == GEAR_NEUTRAL:
                # Motor solto: cai rápido para a marcha lenta
                self.rpm -= 3500 * dt
            else:
                # Engatado: freio motor faz o RPM cair mais devagar
                self.rpm -= 1800 * dt

        # Quando está engatado e sem embreagem, o RPM deve acompanhar as rodas (velocidade)
        if self.current_gear != GEAR_NEUTRAL and not self.clutch_pressed and not self.engine_blown:
            ratio = GEAR_RATIOS[self.current_gear]
            speed_fraction = self.speed / max(1.0, self.top_speed)
            rpm_from_wheels = speed_fraction * RPM_MAX * ratio
            
            # Ajuste suave entre o RPM atual e o RPM que as rodas forçam
            self.rpm = self.rpm * 0.90 + rpm_from_wheels * 0.10

        # Limita o RPM entre zero e o limite máximo mecânico
        self.rpm = max(0.0, min(self.rpm, RPM_MAX))

    def _check_engine_explosion(self, dt):
        """Verifica se o motor passou do limite de segurança (redline) por muito tempo."""
        if self.rpm >= RPM_REDLINE:
            self.redline_timer += dt
            if self.redline_timer >= RPM_EXPLODE_TIME:
                self.engine_blown = True
        else:
            # Reseta o timer de sobreaquecimento lentamente se o motor sair do redline
            self.redline_timer = max(0.0, self.redline_timer - dt * 2)

    def _update_speed(self, dt):
        """Calcula e atualiza a velocidade com base na aceleração e arrasto."""
        if self.current_gear == GEAR_NEUTRAL or self.clutch_pressed:
            # Sem marcha engatada ou com embreagem pisada: o carro perde velocidade pelo atrito natural
            self.speed *= (1.0 - 0.5 * dt)
        else:
            # Carro engatado e acelerando
            if self.gas_pressed and self.rpm > RPM_IDLE:
                # Torque do motor de acordo com a marcha
                gear_torque_mult = {
                    GEAR_FIRST: 2.8,
                    GEAR_SECOND: 2.0,
                    GEAR_THIRD: 1.5,
                    GEAR_FOURTH: 1.15,
                    GEAR_FIFTH: 0.90,
                    GEAR_SIXTH: 0.72,
                    GEAR_REVERSE: 2.2,
                }.get(self.current_gear, 0.0)

                # Eficiência do RPM (motor responde melhor na faixa média de giro)
                rpm_efficiency = min(1.0, self.rpm / 4500.0)
                if self.rpm > 5500:
                    # Perda de rendimento acima das 5500 RPM (incentiva a trocar de marcha)
                    rpm_efficiency *= max(0.7, 1.0 - (self.rpm - 5500) / 3000)

                # Equação simplificada de aceleração
                accel = (self.acceleration_base * self.torque_mult *
                         gear_torque_mult * rpm_efficiency * 60 * dt)
                self.speed += accel

            # Perda de velocidade ao soltar o acelerador
            if not self.gas_pressed:
                self.speed *= (1.0 - 0.3 * dt)

        # Resistência do ar (arrasto aerodinâmico cresce com o quadrado da velocidade)
        drag = (self.speed / self.top_speed) ** 2 * 18 * dt
        self.speed -= drag

        # Limita a velocidade do carro de acordo com a relação da marcha atual
        if self.current_gear != GEAR_NEUTRAL:
            max_speed_gear = self.top_speed * GEAR_SPEED_LIMITS[self.current_gear]
            self.speed = min(self.speed, max_speed_gear)

        # Garante que a velocidade nunca seja negativa
        self.speed = max(0.0, self.speed)

    def apply_grind_penalty(self):
        """Aplica uma penalidade física ao errar a marcha (arranhada de câmbio)."""
        self.rpm *= 0.4      # Motor perde 60% do giro instantaneamente
        self.speed *= 0.85   # O carro perde 15% de velocidade pelo tranco

    @property
    def is_at_redline(self):
        """Informa se o motor está na faixa vermelha do conta-giros."""
        return self.rpm >= RPM_REDLINE

    @property
    def redline_progress(self):
        """Retorna o percentual de 0.0 a 1.0 de perigo de explosão do motor."""
        return min(1.0, self.redline_timer / RPM_EXPLODE_TIME)
