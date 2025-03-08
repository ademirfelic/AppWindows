import os
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from botoes import *
from bannerColeta import *
import requests
import plyer
import pandas as pd

class MyApp(App):

    loja = ''
    lojas = ['Matriz', 'Prudente', 'Cabo Branco', 'Bessa', 'Mossoro','Afonso Pena', 'Princesa Isabel', 'São Paulo']

    def build(self):
        return Builder.load_file('main.kv')

    def on_start(self):
        self.root.ids['lojas'].values = self.lojas

    def opcao_loja(self,spinner,text):
        self.loja = text
    def listar_coletas(self):
        self.excluir_listagem()
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/.json?leitura=1'
        requisicao_dic = requests.get(link).json()
        qnt_coleta = False
        try:
            for dados in requisicao_dic:
                id_usuario = dados
                nome = requisicao_dic[dados]['nome'].upper()
                for coletas in requisicao_dic[dados]['coletas']:
                    leitura = int(requisicao_dic[dados]['coletas'][coletas]['leitura'])
                    if leitura == 0:
                        qnt_coleta = True
                        self.root.ids['notificacao'].text =''
                        qnt = len(requisicao_dic[dados]['coletas'][coletas]['coleta'].split(','))
                        self.root.ids['lista_coleta'].add_widget(
                            BannerColeta(codigo=coletas, nome=nome, quantidade=qnt, id_usuario=id_usuario))
        except:
            pass
        if not qnt_coleta:
            self.root.ids['notificacao'].text = '[color=#FF6666]NÃO HÁ COLETAS[/color]'
            #self.notificacao('não há coleta')

    def baixar_coleta(self, codigo, *args):
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/.json'
        requisicao_dic = requests.get(link).json()
        texto = ''
        for dados in requisicao_dic:
            nome = requisicao_dic[dados]['nome'].upper()
            try:
                for coletas in requisicao_dic[dados]['coletas']:
                    if coletas == codigo:
                        coleta = requisicao_dic[dados]['coletas'][coletas]['coleta'].split(',')
                        for cod in coleta:
                            texto += f'{cod[1:]}                       1\n'

                        diretorio = os.path.isfile(f'../COLETA_{nome}.txt')

                        if diretorio:
                            tempo = str(datetime.now()).replace(':', '').replace('-', '').replace(' ', '')[:14]
                            os.rename(f'../COLETA_{nome}.txt', f'../COLETA_{nome}_{tempo}')

                        with open(f'../COLETA_{nome}.txt', 'w') as arquivo:
                            arquivo.write(texto)
                        self.excluir_coleta(coletas,dados)

            except:
                pass
    def excluir_coleta(self,coletas,dados,*args):
        info = '{"leitura": "1"}'
        requests.patch(
            f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{dados}/coletas/{coletas}.json',
            data=info)
        self.listar_coletas()

    def excluir_listagem(self):
        for item in list(self.root.ids['lista_coleta'].children):
            self.root.ids['lista_coleta'].remove_widget(item)

    def atualizar_tabelas(self):
        self.atualizar_tabela_descricao()
        self.atualizar_tabela_cor()
        atualizado = f'{{"atualizado":"{str(datetime.now())[:-7]}"}}'
        requests.patch(f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabelas/.json',
                       data=atualizado)


    def atualizar_tabela_descricao(self):
        if os.path.isfile('tabela_descricao.csv'):
            produtos = pd.read_csv('tabela_descricao.csv',sep=';', encoding='latin1')
            produtos = produtos.drop_duplicates('Código')
            tabela_descricao =[tuple(linha) for linha in produtos.values]
            info = ''
            i = 0
            for referencia,descricao,valor in tabela_descricao:
                descricao = descricao.replace("\\", "")
                info += f'"{i}":"{referencia}|{descricao}|{valor}",'
                i += 1

            if not requests.post(f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabelas/Tabela_descricao/.json',
                                 data=f'{{{info[:-1]}}}'):
                self.notificacao('erro ao atualizar tabela descriçao')
            else:
                self.notificacao('tabela descricão atualizada')

        else:
            self.notificacao('nao exite tabela descrição a ser atualizada')

    def atualizar_tabela_cor(self):
        if os.path.isfile('tabela_cores.csv'):
            ceres = pd.read_csv('tabela_cores.csv',sep=';', encoding='latin1')
            tabela_cor =[tuple(linha) for linha in ceres.values]
            info = ''
            i = 0
            for codigo,nome in tabela_cor:
                info += f'"{i}":"{codigo}|{nome}",'
                i +=1

            if not requests.post(f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabelas/Tabela_cor/.json',
                                 data=f'{{{info[:-1]}}}'):
                self.notificacao('erro ao atualizar cor tabela')

            else:
                self.notificacao('tabela cor atualizada')

        else:
            self.notificacao('nao exite tabela cor a ser atualizada')

    def notificacao(self, texto):
        plyer.notification.notify(title='Coleta', message=texto)



MyApp().run()