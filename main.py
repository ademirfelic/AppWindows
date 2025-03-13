import os
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from botoes import *
from bannerColeta import *
from telas import *
import requests
import plyer
import pandas as pd

class MyApp(App):
    id_usuario = botao =''
    loja = ''
    lojas = ['Matriz', 'Prudente', 'Cabo Branco', 'Bessa', 'Mossoro','Afonso Pena', 'Princesa Isabel', 'São Paulo']
    tabela = None
    id_tela_anterior = None
    def build(self):
        return Builder.load_file('main.kv')

    def on_start(self):
        self.root.ids['homepage'].ids['lojas'].values = self.lojas
        self.conferir_produto('')

    def mudar_tela(self, id_tela,*args):
        if args:
            id_usuario = args[1]
            id_coleta = args[0]
            self.id_tela_anterior = args[2]
            self.listar_produtos(id_usuario,id_coleta,self.id_tela_anterior)

        self.root.ids['coletapage'].ids['loja_selecionada'].text = f"Loja: {self.root.ids['homepage'].ids['lojas'].text}"
        self.root.ids['historicopage'].ids['loja_historico'].text = \
            f"Historico: {self.root.ids['homepage'].ids['lojas'].text}"

        self.root.ids['coletapage'].ids['notificacao'].text =''
        if self.loja != '':
            self.root.ids['screen_manager'].current = id_tela
        else:
            self.root.ids['homepage'].ids['lojas'].text = '[color=#FF0000]Escolha uma opção[/color]'
    def opcao_loja(self,spinner,text):
        self.loja = text

    def listar_coletas(self,status,id_tela):
        self.loja =self.root.ids['homepage'].ids['lojas'].text
        self.excluir_listagem(id_tela)
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/.json?leitura={status}'
        requisicao_dic = requests.get(link).json()
        qnt_coleta = False
        for dados in requisicao_dic:
            try:
                id_usuario = dados
                nome = requisicao_dic[dados]['nome'].upper()
                for coletas in requisicao_dic[dados]['coletas']:
                    leitura = int(requisicao_dic[dados]['coletas'][coletas]['leitura'])
                    if leitura == status:
                        qnt_coleta = True
                        self.root.ids['coletapage'].ids['notificacao'].text =''
                        qnt = len(requisicao_dic[dados]['coletas'][coletas]['coleta'].split(','))
                        self.root.ids[id_tela].ids['lista_coleta'].add_widget(
                            BannerColeta(codigo=coletas, nome=nome, quantidade=qnt, id_usuario=id_usuario,
                                         status= status,id_tela=id_tela))
            except:
                pass
        if not qnt_coleta:
            self.root.ids['coletapage'].ids['notificacao'].text = '[color=#FF6666]NÃO HÁ COLETAS[/color]'

    def baixar_coleta(self, codigo, id_tela,status,*args):
        self.botao = args[0].source
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
                        self.excluir_coleta(coletas,dados,id_tela,status)

            except:
                pass
    def excluir_coleta(self,coletas,dados,id_tela,status,*args):
        id_tela = self.root.ids['screen_manager'].current
        info = '{"leitura": "1"}'
        if status == 1 and self.botao != 'icones/download.png':
            requests.delete(
                f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{dados}/coletas/{coletas}.json',
                data=info)
        else:
            requests.patch(
                f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{dados}/coletas/{coletas}.json',
                data=info)
        self.listar_coletas(status,id_tela)

    def excluir_listagem(self,id_tela):
        for item in list(self.root.ids[id_tela].ids['lista_coleta'].children):
            self.root.ids[id_tela].ids['lista_coleta'].remove_widget(item)
    def excluir_item(self,item,id_coleta,id_usuario,status,*args):
        coleta = ''
        lista_produto = self.root.ids['produtopage'].ids['lista_coleta']
        id_tela = self.root.ids['screen_manager'].current
        for produto in list(lista_produto.children):
            if produto.id == item:
                lista_produto.remove_widget(produto)
                break
        for produto in list(lista_produto.children):
            coleta += produto.id + ','
        info = f'{{"coleta":"{coleta[:-1]}","leitura":"0"}}'
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{id_usuario}/coletas/{id_coleta}.json'
        requests.patch(link, data=info)
        self.listar_produtos(id_usuario,id_coleta,self.id_tela_anterior)
        self.listar_coletas(status,self.id_tela_anterior)
    def atualizar_tabela(self):

        if os.path.isfile('tabela.csv'):
            produtos = pd.read_csv('tabela.csv',sep=';', encoding='latin1')
            #produtos = produtos.drop_duplicates('Código')
            tabela_descricao =[tuple(linha) for linha in produtos.values]
            info = ''
            i = 0
            for referencia,descricao,cor,grade,valor in tabela_descricao:
                descricao = descricao.replace("\\", "")
                info += f'"{i}":"{referencia}|{descricao}|{valor}|{cor}|{grade}",'
                i += 1

            if not requests.post(f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabela/Tabela/.json',
                                 data=f'{{{info[:-1]}}}'):
                self.root.ids['homepage'].ids['menssagem'].text = '[color=#FF0000]erro ao atualizar tabela[/color]'
            else:
                self.root.ids['homepage'].ids['menssagem'].text = '[color=#00FF00]tabela atualizada[/color]'
                atualizado = f'{{"atualizado":"{str(datetime.now())[:-7]}"}}'
                requests.patch(f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabela/.json',
                               data=atualizado)

        else:
            self.root.ids['homepage'].ids['menssagem'].text = '[color=#FF0000]nao exite tabela a ser atualizada[/color]'
    def atualizar_tabelas(self):
        self.atualizar_tabela_descricao()
        self.atualizar_tabela_cor()
        atualizado = f'{{"atualizado":"{str(datetime.now())[:-7]}"}}'
        requests.patch(f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabelas/.json',
                       data=atualizado)

    def listar_produtos(self,id_usuario,id_coleta, id_tela_anterior):
        self.excluir_listagem('produtopage')
        id_tela = self.root.ids['screen_manager'].current
        link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/{self.loja}/{id_usuario}.json'
        requisicao_dic = requests.get(link).json()
        nome = requisicao_dic['nome'].upper()
        dados = requisicao_dic['coletas'][id_coleta]['coleta'].split(',')
        status = requisicao_dic['coletas'][id_coleta]['leitura']
        self.root.ids['produtopage'].ids['baixar_coleta'].on_release= partial(self.baixar_coleta,id_coleta,1,id_tela)
        self.root.ids['produtopage'].ids['mudar_tela'].on_release = partial(self.mudar_tela,id_tela_anterior)
        for codigo in dados:
            produto = self.conferir_produto(codigo)
            self.root.ids['produtopage'].ids['usuario'].text = f'Usuario:{nome}'
            self.root.ids['produtopage'].ids['lista_coleta'].add_widget(
                BannerProduto(codigo=codigo, cor=produto[0],descricao=produto[1],preco=produto[2],
                              tamanho=produto[3],id_coleta=id_coleta, id_usuario= id_usuario, status = status))
    def conferir_produto(self, codigo):
        cor = descricao = preco = tamanho = ''
        try:
            if not self.tabela:
                link = f'https://appbalanco-27229-default-rtdb.firebaseio.com/Tabela/Tabela.json'
                requisicao_dic = requests.get(link).json()
                dados = requisicao_dic
                for id in dados:
                    self.tabela = dados[id]
            codigo_descricao = codigo[1:7]
            codigo_cor = codigo[7:10]
            codigo_tamanho = int(codigo[10:12]) - 1
            for linha in self.tabela:
                ref, tabela_desc,tabela_preco,tabela_cor,tabela_tamanho = linha.split('|')
                if ref == codigo_descricao and tabela_cor.split('-')[0] == codigo_cor:
                    descricao = tabela_desc
                    preco = tabela_preco
                    cor = tabela_cor.split('-')[1]
                    tamanho = tabela_tamanho.split('/')[codigo_tamanho]
        except:
            pass
        return (cor, descricao, preco, tamanho)

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
                self.root.ids['homepage'].ids['menssagem'].text = '[color=#FF0000]erro ao atualizar tabela descriçao[/color]'
            else:
                self.root.ids['homepage'].ids['menssagem'].text = '[color=#00FF00]tabela descricão atualizada[/color]'

        else:
            self.root.ids['homepage'].ids['menssagem'].text = '[color=#FF0000]nao exite tabela descrição a ser atualizada[/color]'

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
                self.root.ids['homepage'].ids['menssagem'].text = '[color=#FF0000]erro ao atualizar cor tabela[/color]'

            else:
                self.root.ids['homepage'].ids['menssagem'].text = '[color=#00FF00]tabela cor atualizada[/color]'

        else:
            self.root.ids['homepage'].ids['menssagem'].text = '[color=#FF0000]nao exite tabela cor a ser atualizada[/color]'

    def notificacao(self, texto):
        plyer.notification.notify(title='Coleta', message=texto)



MyApp().run()