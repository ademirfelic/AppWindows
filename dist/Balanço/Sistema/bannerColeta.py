from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.app import App
from botoes import *
from functools import partial

class BannerColeta(GridLayout):

    def __init__(self,**kwargs):
        self.rows = 1
        super().__init__()
        with self.canvas:
            Color(rgb=(0,0,0,1))
            self.rec = Rectangle(size= self.size, pos= self.pos)

        self.bind(pos=self.atualiza_rec, size=self.atualiza_rec)

        codigo = kwargs['codigo']
        nome = kwargs['nome']
        quantidade = kwargs['quantidade']
        self.id = codigo
        coleta = FloatLayout()
        label_nome = Label(text=f'Nome: {nome}', pos_hint={'right': 0.55, 'top': 0.95}, size_hint=(0.58, 0.33))
        label_qnt = Label(text=f'Quantidade: {quantidade}', pos_hint={'right': 0.55, 'top': 0.60}, size_hint=(0.2 , 0.33))

        app = App.get_running_app()
        imagem = ImageButton(source='icones/download.png',
                             pos_hint={"right": 1, "top": 0.90}, size_hint=(0.12, 0.5),
                             on_release=partial(app.baixar_coleta,codigo))

        coleta.add_widget(label_nome)
        coleta.add_widget(label_qnt)
        coleta.add_widget(imagem)

        self.add_widget(coleta)


    def atualiza_rec(self,*args):
        self.rec.pos = self.pos
        self.rec.size = self.size