import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.camera import Camera
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.logger import Logger

import cv2
import numpy as np
import sqlite3
import os
import threading
from datetime import datetime

from database import Database
from face_recognition import FaceRecognizer
from tts_engine import TTSEngine

Builder.load_string('''
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: 'PORTARIA FACIAL'
            font_size: 32
            bold: True
            size_hint_y: 0.2
            color: 0, 0.5, 1, 1
        Button:
            text: 'RECONHECER (PORTARIA)'
            font_size: 24
            size_hint_y: 0.18
            background_color: 0, 0.7, 0.2, 1
            on_press: root.go_recognize()
        Button:
            text: 'CADASTRAR MORADOR'
            font_size: 24
            size_hint_y: 0.18
            background_color: 0.2, 0.5, 1, 1
            on_press: root.go_register()
        Button:
            text: 'LISTAR MORADORES'
            font_size: 24
            size_hint_y: 0.18
            background_color: 1, 0.6, 0, 1
            on_press: root.go_list()
        Button:
            text: 'CONFIGURACOES'
            font_size: 24
            size_hint_y: 0.18
            background_color: 0.5, 0.3, 0.8, 1
            on_press: root.go_settings()
        Label:
            text: 'Offline | FaceNet + SQLite + TTS'
            font_size: 14
            size_hint_y: 0.08
            color: 0.6, 0.6, 0.6, 1

<RecognizeScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            id: status_label
            text: 'Aguardando rosto...'
            font_size: 22
            size_hint_y: 0.1
            color: 1, 1, 1, 1
        Camera:
            id: camera
            resolution: (640, 480)
            play: True
            size_hint_y: 0.6
        Label:
            id: info_label
            text: ''
            font_size: 18
            size_hint_y: 0.15
            color: 0, 1, 0.5, 1
            text_size: self.width, None
            halign: 'center'
            valign: 'middle'
        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            Button:
                text: 'VOLTAR'
                font_size: 20
                background_color: 0.8, 0.2, 0.2, 1
                on_press: root.go_back()

<RegisterScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'CADASTRAR MORADOR'
            font_size: 26
            bold: True
            size_hint_y: 0.1
            color: 0, 0.5, 1, 1
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'Nome Completo:'
                font_size: 18
                size_hint_y: 0.4
                halign: 'left'
                text_size: self.width, None
            TextInput:
                id: nome_input
                hint_text: 'Ex: Joao da Silva'
                font_size: 18
                multiline: False
                size_hint_y: 0.6
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'CPF (apenas numeros):'
                font_size: 18
                size_hint_y: 0.4
                halign: 'left'
                text_size: self.width, None
            TextInput:
                id: cpf_input
                hint_text: 'Ex: 12345678901'
                font_size: 18
                multiline: False
                input_filter: 'int'
                size_hint_y: 0.6
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'Tipo:'
                font_size: 18
                size_hint_y: 0.4
                halign: 'left'
                text_size: self.width, None
            BoxLayout:
                spacing: 10
                size_hint_y: 0.6
                ToggleButton:
                    id: tipo_morador
                    text: 'Morador'
                    group: 'tipo'
                    state: 'down'
                    font_size: 18
                ToggleButton:
                    id: tipo_visitante
                    text: 'Visitante'
                    group: 'tipo'
                    font_size: 18
                ToggleButton:
                    id: tipo_funcionario
                    text: 'Funcionario'
                    group: 'tipo'
                    font_size: 18
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'Bloco/Apartamento:'
                font_size: 18
                size_hint_y: 0.4
                halign: 'left'
                text_size: self.width, None
            TextInput:
                id: unidade_input
                hint_text: 'Ex: Bloco A - Ap 101'
                font_size: 18
                multiline: False
                size_hint_y: 0.6
        Camera:
            id: reg_camera
            resolution: (640, 480)
            play: True
            size_hint_y: 0.25
        BoxLayout:
            spacing: 10
            size_hint_y: 0.1
            Button:
                text: 'CAPTURAR ROSTO'
                font_size: 20
                background_color: 0, 0.7, 0.2, 1
                on_press: root.capture_face()
            Button:
                text: 'VOLTAR'
                font_size: 20
                background_color: 0.8, 0.2, 0.2, 1
                on_press: root.go_back()
        Label:
            id: reg_status
            text: 'Posicione o rosto no quadro e toque CAPTURAR'
            font_size: 16
            size_hint_y: 0.1
            color: 1, 1, 0, 1

<ListScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: 'MORADORES CADASTRADOS'
            font_size: 26
            bold: True
            size_hint_y: 0.08
            color: 0, 0.5, 1, 1
        ScrollView:
            BoxLayout:
                id: lista_container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: 5
                spacing: 5
        Button:
            text: 'VOLTAR'
            font_size: 20
            size_hint_y: 0.08
            background_color: 0.8, 0.2, 0.2, 1
            on_press: root.go_back()

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 15
        Label:
            text: 'CONFIGURACOES'
            font_size: 26
            bold: True
            size_hint_y: 0.1
            color: 0, 0.5, 1, 1
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'Limiar de Similaridade (0.0 - 1.0):'
                font_size: 18
                halign: 'left'
                text_size: self.width, None
            Slider:
                id: threshold_slider
                min: 0.3
                max: 0.9
                value: 0.6
                step: 0.05
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'Frase de Liberacao:'
                font_size: 18
                halign: 'left'
                text_size: self.width, None
            TextInput:
                id: frase_input
                hint_text: 'Acesso liberado, {nome}'
                font_size: 18
                multiline: False
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.15
            spacing: 5
            Label:
                text: 'Frase de Negado:'
                font_size: 18
                halign: 'left'
                text_size: self.width, None
            TextInput:
                id: frase_negado_input
                hint_text: 'Acesso negado. Nao cadastrado.'
                font_size: 18
                multiline: False
        BoxLayout:
            spacing: 10
            size_hint_y: 0.1
            Button:
                text: 'SALVAR'
                font_size: 20
                background_color: 0, 0.7, 0.2, 1
                on_press: root.save_settings()
            Button:
                text: 'VOLTAR'
                font_size: 20
                background_color: 0.8, 0.2, 0.2, 1
                on_press: root.go_back()

<MoradorItem@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: 60
    padding: 10
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.nome
        font_size: 18
        halign: 'left'
        valign: 'middle'
        text_size: self.width * 0.6, None
        color: 1, 1, 1, 1
    Label:
        text: root.cpf
        font_size: 16
        halign: 'center'
        valign: 'middle'
        text_size: self.width * 0.2, None
        color: 0.8, 0.8, 0.8, 1
    Label:
        text: root.tipo
        font_size: 16
        halign: 'center'
        valign: 'middle'
        text_size: self.width * 0.2, None
        color: 0, 1, 0.5, 1
''')

class MenuScreen(Screen):
    def go_recognize(self):
        self.manager.current = 'recognize'
        self.manager.get_screen('recognize').start_recognition()

    def go_register(self):
        self.manager.current = 'register'

    def go_list(self):
        self.manager.current = 'list'
        self.manager.get_screen('list').load_list()

    def go_settings(self):
        self.manager.current = 'settings'
        self.manager.get_screen('settings').load_settings()

class RecognizeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recognizer = None
        self.db = None
        self.tts = None
        self.running = False
        self.last_spoken = 0
        self.cooldown = 3.0

    def on_enter(self):
        self.recognizer = FaceRecognizer()
        self.db = Database()
        self.tts = TTSEngine()
        self.running = True
        Clock.schedule_interval(self.process_frame, 1.0/10.0)

    def on_leave(self):
        self.running = False
        Clock.unschedule(self.process_frame)
        if self.recognizer:
            self.recognizer.release()

    def start_recognition(self):
        self.ids.status_label.text = 'Camera ativa - Aguardando rosto...'
        self.ids.info_label.text = ''

    def process_frame(self, dt):
        if not self.running:
            return
        camera = self.ids.camera
        if not camera.texture:
            return
        try:
            frame = self.texture_to_frame(camera.texture)
            if frame is None:
                return
            result = self.recognizer.recognize(frame, self.db)
            if result:
                pessoa, similarity = result
                now = datetime.now().timestamp()
                if now - self.last_spoken > self.cooldown:
                    self.last_spoken = now
                    self.show_result(pessoa, similarity)
                    self.speak_result(pessoa, similarity)
            else:
                self.ids.status_label.text = 'Procurando rosto...'
                self.ids.info_label.text = ''
        except Exception as e:
            Logger.error(f'Portaria: {e}')

    def texture_to_frame(self, texture):
        buf = texture.pixels
        if not buf:
            return None
        img = np.frombuffer(buf, np.uint8).reshape(texture.height, texture.width, 4)
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    def show_result(self, pessoa, similarity):
        if pessoa:
            self.ids.status_label.text = f'RECONHECIDO: {pessoa["nome"]}'
            self.ids.info_label.text = f'CPF: {pessoa["cpf"]}\nTipo: {pessoa["tipo"]}\nUnidade: {pessoa["unidade"]}\nSimilaridade: {similarity:.2%}'
        else:
            self.ids.status_label.text = 'NAO RECONHECIDO'
            self.ids.info_label.text = 'Pessoa nao cadastrada ou similaridade baixa'

    def speak_result(self, pessoa, similarity):
        settings = self.db.get_settings()
        if pessoa and similarity >= settings['threshold']:
            frase = settings['frase_liberacao'].format(nome=pessoa['nome'])
            self.tts.speak(frase)
        else:
            self.tts.speak(settings['frase_negado'])

    def go_back(self):
        self.manager.current = 'menu'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recognizer = None
        self.db = None
        self.captured_embedding = None

    def on_enter(self):
        self.recognizer = FaceRecognizer()
        self.db = Database()

    def on_leave(self):
        if self.recognizer:
            self.recognizer.release()

    def capture_face(self):
        camera = self.ids.reg_camera
        if not camera.texture:
            self.ids.reg_status.text = 'Camera nao pronta'
            return
        frame = self.texture_to_frame(camera.texture)
        if frame is None:
            self.ids.reg_status.text = 'Erro ao capturar'
            return
        embedding = self.recognizer.get_embedding(frame)
        if embedding is None:
            self.ids.reg_status.text = 'Rosto nao detectado. Tente novamente.'
            return
        self.captured_embedding = embedding
        self.ids.reg_status.text = 'Rosto capturado! Preencha os dados e toque SALVAR (abaixo)'
        self.save_registration()

    def save_registration(self):
        nome = self.ids.nome_input.text.strip()
        cpf = self.ids.cpf_input.text.strip()
        unidade = self.ids.unidade_input.text.strip()
        tipo = 'Morador'
        if self.ids.tipo_visitante.state == 'down':
            tipo = 'Visitante'
        elif self.ids.tipo_funcionario.state == 'down':
            tipo = 'Funcionario'

        if not nome or not cpf or len(cpf) != 11:
            self.show_popup('Erro', 'Preencha nome e CPF (11 digitos)')
            return
        if self.captured_embedding is None:
            self.show_popup('Erro', 'Capture o rosto primeiro')
            return

        try:
            self.db.add_person(nome, cpf, tipo, unidade, self.captured_embedding)
            self.show_popup('Sucesso', f'{nome} cadastrado com sucesso!')
            self.clear_form()
        except Exception as e:
            self.show_popup('Erro', f'Falha ao salvar: {e}')

    def clear_form(self):
        self.ids.nome_input.text = ''
        self.ids.cpf_input.text = ''
        self.ids.unidade_input.text = ''
        self.ids.tipo_morador.state = 'down'
        self.captured_embedding = None
        self.ids.reg_status.text = 'Posicione o rosto no quadro e toque CAPTURAR'

    def texture_to_frame(self, texture):
        buf = texture.pixels
        if not buf:
            return None
        img = np.frombuffer(buf, np.uint8).reshape(texture.height, texture.width, 4)
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg, font_size=18),
                      size_hint=(0.8, 0.4))
        popup.open()

    def go_back(self):
        self.manager.current = 'menu'

class ListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()

    def load_list(self):
        container = self.ids.lista_container
        container.clear_widgets()
        pessoas = self.db.get_all_people()
        for p in pessoas:
            item = BoxLayout(orientation='horizontal', size_hint_y=None, height=60,
                            padding=10, spacing=10)
            with item.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.15, 0.15, 0.2, 1)
                rect = Rectangle(pos=item.pos, size=item.size)
            item.bind(pos=lambda i, v: setattr(rect, 'pos', i.pos),
                      size=lambda i, v: setattr(rect, 'size', i.size))

            item.add_widget(Label(text=p['nome'], font_size=18, halign='left',
                                 valign='middle', text_size=(None, None),
                                 color=(1,1,1,1), size_hint_x=0.5))
            item.add_widget(Label(text=p['cpf'], font_size=16, halign='center',
                                 valign='middle', color=(0.8,0.8,0.8,1),
                                 size_hint_x=0.25))
            item.add_widget(Label(text=p['tipo'], font_size=16, halign='center',
                                 valign='middle', color=(0,1,0.5,1),
                                 size_hint_x=0.25))
            container.add_widget(item)

    def go_back(self):
        self.manager.current = 'menu'

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()

    def on_enter(self):
        self.load_settings()

    def load_settings(self):
        s = self.db.get_settings()
        self.ids.threshold_slider.value = s['threshold']
        self.ids.frase_input.text = s['frase_liberacao']
        self.ids.frase_negado_input.text = s['frase_negado']

    def save_settings(self):
        threshold = self.ids.threshold_slider.value
        frase = self.ids.frase_input.text.strip() or 'Acesso liberado, {nome}'
        frase_negado = self.ids.frase_negado_input.text.strip() or 'Acesso negado. Nao cadastrado.'
        self.db.save_settings(threshold, frase, frase_negado)
        self.show_popup('Salvo', 'Configuracoes atualizadas')

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg, font_size=18),
                      size_hint=(0.8, 0.4))
        popup.open()

    def go_back(self):
        self.manager.current = 'menu'

class PortariaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(RecognizeScreen(name='recognize'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ListScreen(name='list'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def on_stop(self):
        pass

if __name__ == '__main__':
    PortariaApp().run()