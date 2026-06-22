"""
Módulo de gerenciamento de áudio
Carrega e reproduz arquivos de som .wav e .mp3 de forma direta e didática
"""

import os
import pygame

class SoundManager:
    """
    Gerenciador de som simples que carrega arquivos de áudio
    Permite reproduzir efeitos sonoros pontuais e gerenciar o som do motor em loop por marcha
    Suporta controle de volume global
    """

    def __init__(self):
        """Inicializa o mixer de áudio e carrega os efeitos sonoros disponíveis"""
        # Inicializa o mixer se necessário
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Volume geral padrão (de 0.0 a 1.0)
        self.volume = 0.1

        # Canal exclusivo para o som do motor do jogador
        self.engine_channel = pygame.mixer.Channel(1)
        self.engine_channel.set_volume(self.volume)
        self.current_playing_gear = None

        # Dicionário para armazenar os efeitos sonoros pontuais do pygame
        self.sounds = {}

        # Mapeamento de nomes de som para seus respectivos arquivos
        sound_files = {
            "gear_shift": "assets/sounds/shift.mp3",
            "gear_grind": "assets/sounds/scratchedGearbox.mp3",
            "countdown_beep": "assets/sounds/countdown_beep.mp3",
            "countdown_go": "assets/sounds/countdown_go.mp3",
            "win": "assets/sounds/win.mp3",
            "lose": "assets/sounds/lose.mp3",
            "explosion": "assets/sounds/explosion.mp3",
        }

        # Carrega os arquivos diretamente
        for name, path in sound_files.items():
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.volume)
            self.sounds[name] = sound

        # Carrega os arquivos de áudio dos motores por marcha (.mp3)
        self.gear_sounds = {}
        for gear in range(1, 7):
            filename = self._get_gear_filename(gear)
            path = f"assets/sounds/{filename}"
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.volume)
            self.gear_sounds[gear] = sound

    def _get_gear_filename(self, gear):
        """Retorna o nome do arquivo MP3 correspondente à marcha"""
        mapping = {
            1: "firstGear.mp3",
            2: "secondGear.mp3",
            3: "thirdGear.mp3",
            4: "fourthGear.mp3",
            5: "fifthGear.mp3",
            6: "sixthGear.mp3",
        }

        return mapping.get(gear, "")

    def play(self, sound_name):
        """Toca um efeito sonoro de disparo único (one-shot)"""
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            self.sounds[sound_name].play()

    def update_engine_sound(self, gear, clutch_pressed):
        """
        Atualiza o som de loop do motor de acordo com a marcha e embreagem do jogador
        Para o som se o jogador segurar a embreagem ou estiver em Neutro/Ré
        """
        # Se a embreagem estiver pressionada ou estiver em Neutro (0) / Ré (-1)
        if clutch_pressed or gear <= 0:
            if self.engine_channel.get_busy():
                self.engine_channel.stop()
                self.current_playing_gear = None

            return

        # Se mudou de marcha ou o som estava parado
        if self.current_playing_gear != gear:
            sound = self.gear_sounds.get(gear)

            if sound:
                # Para o som anterior se houver
                if self.engine_channel.get_busy():
                    self.engine_channel.stop()

                # Toca o novo som em loop (-1 indica reprodução contínua)
                self.engine_channel.play(sound, loops=-1)
                self.current_playing_gear = gear

    def stop_engine_sound(self):
        """Interrompe qualquer som de motor em reprodução"""
        if self.engine_channel.get_busy():
            self.engine_channel.stop()

        self.current_playing_gear = None

    def set_volume(self, volume):
        """
        Define o volume geral de todos os sons do jogo
        :param volume: Float entre 0.0 (mudo) e 1.0 (máximo)
        """
        self.volume = max(0.0, min(1.0, volume))
        self.engine_channel.set_volume(self.volume)

        # Atualiza o volume de todos os sons pontuais
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.volume)

        # Atualiza o volume de todos os sons de motor por marcha
        for sound in self.gear_sounds.values():
            if sound is not None:
                sound.set_volume(self.volume)

