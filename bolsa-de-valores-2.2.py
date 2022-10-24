from tkinter import *
import sqlite3
from tkinter import scrolledtext, ttk, messagebox
from tkcalendar import Calendar, DateEntry

janela = Tk()

class funcoes:
    def calculo_taxa_b3(self):
        quant_acoes = float(self.entrada_qtd_acoes.get())
        valor_unit = float(self.entrada_valor_unitario.get())
        return round(0.0003 * quant_acoes * valor_unit, 2)

    def calculo_operacao(self):
        valor_taxa_b3 = self.calculo_taxa_b3()

        if self.entrada_tipo_operacao.get() == 'COMPRA':
            return round(float(self.entrada_qtd_acoes.get()) * float(self.entrada_valor_unitario.get()) + float(self.entrada_taxa_corretagem.get()) + valor_taxa_b3, 2)
        if self.entrada_tipo_operacao.get() == 'VENDA':
            return round(float(self.entrada_qtd_acoes.get()) * float(self.entrada_valor_unitario.get()) - float(self.entrada_taxa_corretagem.get()) + valor_taxa_b3, 2)

    def calculo_preco_medio(self):
        self.conectar_banco()
        quant = int(list(self.cursor.execute(f"SELECT COUNT(codigo_operacao) AS quantidade FROM operacoes WHERE codigo_operacao = '{self.entrada_codigo_ativo.get()}' AND tipo_operacao = 'COMPRA';"))[0][0])
        if quant == 0:
            self.desconectar_banco()
            if self.entrada_tipo_operacao.get() == "COMPRA":
                return round(float(self.calculo_operacao())/float(self.entrada_qtd_acoes.get()), 2)
            return 0
        preco_ant = list(self.cursor.execute(f"SELECT preco_medio FROM operacoes GROUP BY id_operacao HAVING codigo_operacao = '{self.entrada_codigo_ativo.get()}' AND tipo_operacao = 'COMPRA' ;"))[-1][0]
        self.desconectar_banco()
        if self.entrada_tipo_operacao.get() == "COMPRA":
            return round((float(self.calculo_operacao())/float(self.entrada_qtd_acoes.get()) + float(preco_ant))/2.0, 2)
        return float(preco_ant)

    def limpar_tela(self):
        self.entrada_id_operacao.delete(0, END)
        self.entrada_data.delete(0, END)
        self.entrada_qtd_acoes.delete(0, END)
        self.entrada_valor_unitario.delete(0, END)
        self.entrada_taxa_corretagem.delete(0, END)

    def conectar_banco(self):
        self.conector = sqlite3.connect('bolsa_de_valores.bd')
        self.cursor = self.conector.cursor()
        print('Conectando-se ao banco de dados...')

    def desconectar_banco(self):
        self.conector.close()
        print('Banco de dados desconectado...')

    def criar_tabela(self):
        self.conectar_banco()

        # criação da tabela operações
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS operacoes (
            id_operacao INTEGER PRIMARY KEY,
            codigo_operacao VARCHAR(10) NOT NULL,
            data DATE NOT NULL,
            qtd_acoes INTEGER NOT NULL,
            valor_unitario FLOAT NOT NULL,
            tipo_operacao CHAR(6) NOT NULL,
            taxa_corretagem FLOAT NOT NULL,
            taxa_b3 FLOAT NOT NULL,
            valor_operacao FLOAT NOT NULL,
            preco_medio FLOAT NOT NULL
        );''')
        self.conector.commit()
        print('Banco de dados criado com sucesso!')
        self.desconectar_banco()

    def variaveis(self):
        self.id_oper = self.entrada_id_operacao.get()
        self.cod_ativo = self.entrada_codigo_ativo.get()
        self.data = self.entrada_data.get()
        self.qtd = self.entrada_qtd_acoes.get()
        self.valor_unt = self.entrada_valor_unitario.get()
        self.tipo_op = self.entrada_tipo_operacao.get().upper()
        self.taxa_corr = self.entrada_taxa_corretagem.get()
        self.tx_b3 = self.calculo_taxa_b3()
        self.valor_op = self.calculo_operacao()
        self.preco_medio = self.calculo_preco_medio()

    def adicionar_operacao(self):
        self.variaveis()

        # comando não é executado por que dá problema no cálculo da taxa da B3
        if self.id_oper == None and self.cod_ativo == None and self.data == None and self.qtd == None and self.valor_unt == None and self.tipo_op == None and self.taxa_corr == None:
            mensagem = 'Para cadastrar uma operação, preencha todos os campos obrigatórios!'
            messagebox.showinfo('Informação de Erro', mensagem)
        else:
            self.conectar_banco()

            self.cursor.execute('''INSERT INTO operacoes(codigo_operacao, data, qtd_acoes, valor_unitario, tipo_operacao, taxa_corretagem, taxa_b3, valor_operacao, preco_medio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.cod_ativo, self.data, self.qtd, self.valor_unt, self.tipo_op, self.taxa_corr, self.tx_b3, self.valor_op, self.preco_medio))
            self.conector.commit()
            self.desconectar_banco()
            self.select_lista()
            self.limpar_tela()

    def select_lista(self):
        self.lista_operacoes.delete(*self.lista_operacoes.get_children())
        self.conectar_banco()
        lista = self.cursor.execute('''SELECT id_operacao, codigo_operacao, data, qtd_acoes, valor_unitario, tipo_operacao, taxa_corretagem, taxa_b3, valor_operacao, preco_medio FROM operacoes
                ORDER BY id_operacao ASC
            ''')
        for elemento in lista:
            self.lista_operacoes.insert('', END, values=elemento)
        self.desconectar_banco()

    def duplo_clique(self, event):
        self.limpar_tela()
        self.lista_operacoes.selection()

        for termo in self.lista_operacoes.selection():
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = self.lista_operacoes.item(termo, 'values')
            self.entrada_id_operacao.insert(END, col1)
            self.entrada_codigo_ativo.set(col2)
            self.entrada_data.insert(END, col3)
            self.entrada_qtd_acoes.insert(END, col4)
            self.entrada_valor_unitario.insert(END, col5)
            self.entrada_tipo_operacao.set(col6)
            self.entrada_taxa_corretagem.insert(END, col7)

    def apagar_operacao(self):
        self.variaveis()
        self.conectar_banco()
        self.conector.execute('''DELETE FROM operacoes WHERE id_operacao = ?''', (self.id_oper))
        self.conector.commit()
        self.desconectar_banco()
        self.limpar_tela()
        self.select_lista()

    def alterar_operacao(self):
        self.variaveis()
        self.conectar_banco()
        self.cursor.execute('''UPDATE operacoes SET codigo_operacao = ?, data = ?, qtd_acoes = ?, valor_unitario = ?, tipo_operacao = ?, taxa_corretagem = ?, taxa_b3 = ?, valor_operacao = ?, preco_medio = ?
            WHERE id_operacao = ?
        ''', (self.cod_ativo, self.data, self.qtd, self.valor_unt, self.tipo_op, self.taxa_corr, self.tx_b3, self.valor_op, self.preco_medio, self.id_oper))
        self.conector.commit()
        self.desconectar_banco()
        self.select_lista()
        self.limpar_tela()

    def buscar_operacao(self):
        self.conectar_banco()
        self.lista_operacoes.delete(*self.lista_operacoes.get_children())

        cod_do_ativo = self.entrada_codigo_ativo.get()
        self.cursor.execute("""SELECT id_operacao, codigo_operacao, data, qtd_acoes, valor_unitario, tipo_operacao, taxa_corretagem, taxa_b3, valor_operacao, preco_medio FROM operacoes
                        WHERE codigo_operacao LIKE '%s' ORDER BY codigo_operacao ASC
                    """ % cod_do_ativo)

        buscar_ativo = self.cursor.fetchall()
        for op in buscar_ativo:
            self.lista_operacoes.insert('', END, values=op)
        self.limpar_tela()
        self.desconectar_banco()

    def exibir_calendario(self):
        self.calendario = Calendar(self.aba1, fg='gray75', bg='blue', font=('verdana', 8, 'bold'), locale='pt_br')
        self.calendario.place(relx=0.5, rely=0.1)
        self.gravar_data = Button(self.aba1, text='Inserir data', bd=2, bg='red', fg='white', font=('verdana', 8, 'bold'), command=self.imprimir_data)
        self.gravar_data.place(relx=0.26, rely=0.64, relheight=0.10)

    def imprimir_data(self):
        data = self.calendario.get_date()
        self.calendario.destroy()
        self.entrada_data.delete(0, END)
        self.entrada_data.insert(END, data)
        self.gravar_data.destroy()

class aplicativo(funcoes):
    def __init__(self):
        self.janela = janela
        self.tela()
        self.frames_de_tela()
        self.widgets_frame_1()
        self.widgets_frame_2()
        self.criar_tabela()
        self.select_lista()
        self.menus()
        janela.mainloop()

    def tela(self):
        # título da janela: aparece logo na barra de título
        self.janela.title('Cadastro de Operações')
        self.janela.configure(background='#1e3743')  # cor de fundo da janela
        # tamanho inicial da janela altura = 700 x largura = 500
        self.janela.geometry('700x500')
        # responsividade da tela, True True quer dizer que a tela vai ser responsiva na altura e na largura
        self.janela.resizable(True, True)
        # cria um limite máximo de tamanho que a janela pode ter, nesse caso 900x700
        self.janela.maxsize(width=900, height=700)
        # cria um limite mínimo de tamanho que a janela pode ter, nesse caso 400x300
        self.janela.minsize(width=700, height=500)

    def frames_de_tela(self):
        # criação dos frames dentro da janela
        self.frame_1 = Frame(self.janela, bd=4, bg='#dfe3ee',
                             highlightbackground='#759fe6', highlightthickness=3)
        self.frame_1.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.47)

        self.frame_2 = Frame(self.janela, bd=4, bg='#dfe3ee',
                             highlightbackground='#759fe6', highlightthickness=3)
        self.frame_2.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.46)

    def widgets_frame_1(self):
        # ABAS =================================================================================
        self.abas = ttk.Notebook(self.frame_1)
        self.aba1 = Frame(self.abas)
        self.aba2 = Frame(self.abas)

        self.aba1.configure(background='#dfe3ee')
        self.aba2.configure(background='#dfe3ee')

        self.abas.add(self.aba1, text='Aba 1')
        self.abas.add(self.aba2, text='Aba 2')

        self.abas.place(relx=0, rely=0, relwidth=1.001, relheight=1.01)

        # BOTÕES =================================================================================
        # criação do botão limpar
        self.btn_limpar = Button(self.aba1, text='Limpar', bd=2, bg='#107db2', fg='white', font=(
            'verdana', 8, 'bold'), command=self.limpar_tela)
        self.btn_limpar.place(relx=0.3, rely=0.1, relwidth=0.1, relheight=0.15)

        # criação do botão buscar
        self.btn_buscar = Button(self.aba1, text='Buscar', bd=2, bg='#107db2', fg='white', font=(
            'verdana', 8, 'bold'), command=self.buscar_operacao)
        self.btn_buscar.place(relx=0.4, rely=0.1, relwidth=0.1, relheight=0.15)

        # criação do botão novo
        self.btn_guardar = Button(self.aba1, text='Guardar', bd=2, bg='#107db2', fg='white', font=(
            'verdana', 8, 'bold'), command=self.adicionar_operacao)
        self.btn_guardar.place(
            relx=0.6, rely=0.1, relwidth=0.1, relheight=0.15)

        # criação do botão alterar
        self.btn_alterar = Button(self.aba1, text='Alterar', bd=2, bg='#107db2', fg='white', font=(
            'verdana', 8, 'bold'), command=self.alterar_operacao)
        self.btn_alterar.place(
            relx=0.7, rely=0.1, relwidth=0.1, relheight=0.15)

        # criação do botão apagar
        self.btn_apagar = Button(self.aba1, text='Apagar', bd=2, bg='#107db2', fg='white', font=(
            'verdana', 8, 'bold'), command=self.apagar_operacao)
        self.btn_apagar.place(relx=0.8, rely=0.1, relwidth=0.1, relheight=0.15)

        # LABELS =================================================================================

        # criação do label ID operação
        self.label_id_operacao = Label(
            self.aba1, text='ID Oper.', bg='#dfe3ee', fg='#1e3743')
        self.label_id_operacao.place(relx=0.19, rely=0.05)

        self.entrada_id_operacao = Entry(self.aba1)
        self.entrada_id_operacao.place(relx=0.19, rely=0.15, relwidth=0.10)

        # criação do label código ativo
        self.label_codigo_ativo = Label(self.aba1, text='Cód. Ativo', bg='#dfe3ee', fg='#1e3743')
        self.label_codigo_ativo.place(relx=0.05, rely=0.05)

        self.entrada_codigo_ativo = StringVar(self.aba1)
        self.ativos = ('VALE3', 'PETR4', 'ELET3', 'ITUB4', 'BBSA3', 'PETR3', 'B3SA3', 'BBDC4', 'CIEL3', 'NTCO3', 'TIMS3')
        self.entrada_codigo_ativo.set('VALE3')
        self.popup_menu_ativos = OptionMenu(self.aba1, self.entrada_codigo_ativo, *self.ativos)
        self.popup_menu_ativos.place(relx=0.05, rely=0.15, relwidth=0.13, relheight=0.12)

        # criação do label quantidade de ações
        self.label_qtd_acoes = Label(
            self.aba1, text='Quantidade de Ações', bg='#dfe3ee', fg='#1e3743')
        self.label_qtd_acoes.place(relx=0.05, rely=0.31)

        self.entrada_qtd_acoes = Entry(self.aba1)
        self.entrada_qtd_acoes.place(relx=0.05, rely=0.41, relwidth=0.4)

        # criação do label valor unitário
        self.label_valor_unitario = Label(
            self.aba1, text='Valor Unitário', bg='#dfe3ee', fg='#1e3743')
        self.label_valor_unitario.place(relx=0.5, rely=0.31)

        self.entrada_valor_unitario = Entry(self.aba1)
        self.entrada_valor_unitario.place(relx=0.5, rely=0.41, relwidth=0.4)

        # criação do label data com calendário
        self.label_data = Label(self.aba1, text='Data', bg='#dfe3ee', fg='#1e3743')
        self.label_data.place(relx=0.05, rely=0.54)

        self.botao_data = Button(self.aba1, text='Selecione', bd=2, bg='#107db2', fg='white', font=('verdana', 8, 'bold'), command=self.exibir_calendario)
        self.botao_data.place(relx=0.26, rely=0.64, relheight=0.10)

        self.entrada_data = Entry(self.aba1, width=10)
        self.entrada_data.place(relx=0.05, rely=0.64, relwidth=0.2)

        # criação do label tipo de operação
        self.label_tipo_operacao = Label(
            self.aba1, text='Tipo de Operação', bg='#dfe3ee', fg='#1e3743')
        self.label_tipo_operacao.place(relx=0.5, rely=0.54)

        self.entrada_tipo_operacao = StringVar(self.aba1)
        self.opcoes = ('COMPRA', 'VENDA')
        self.entrada_tipo_operacao.set('COMPRA')
        self.popup_menu_tipo_op = OptionMenu(self.aba1, self.entrada_tipo_operacao, *self.opcoes)
        self.popup_menu_tipo_op.place(relx=0.5, rely=0.64, relwidth=0.4, relheight=0.13)

        # criação do label taxa corretagem
        self.label_taxa_corretagem = Label(
            self.aba1, text='Taxa Corretagem', bg='#dfe3ee', fg='#1e3743')
        self.label_taxa_corretagem.place(relx=0.05, rely=0.78)

        self.entrada_taxa_corretagem = Entry(self.aba1)
        self.entrada_taxa_corretagem.place(relx=0.05, rely=0.88, relwidth=0.2)

        # criação do label taxa B3
        '''self.label_taxa_b3 = Label(
            self.aba1, text='Taxa B3', bg='#dfe3ee', fg='#1e3743')
        self.label_taxa_b3.place(relx=0.5, rely=0.78)

        self.entrada_taxa_b3 = Entry(self.aba1)
        self.entrada_taxa_b3.place(relx=0.5, rely=0.88, relwidth=0.2)'''

        # criação do label preço médio atual
        self.label_preco_medio_atual = Label(
            self.aba1, text='Preço Médio Atual', bg='#dfe3ee', fg='#1e3743')
        self.label_preco_medio_atual.place(relx=0.5, rely=0.78)

        self.entrada_preco_medio_atual = Entry(self.aba1)
        self.entrada_preco_medio_atual.place(relx=0.5, rely=0.88, relwidth=0.2)

    def widgets_frame_2(self):
        # LISTAGEM COM A EXIBIÇÃO DOS DADOS
        self.lista_operacoes = ttk.Treeview(self.frame_2, height=3, column=('coluna1', 'coluna2', 'coluna3', 'coluna4', 'coluna5', 'coluna6', 'coluna7', 'coluna8', 'coluna9', 'coluna10'))
        self.lista_operacoes.heading('#0', text='')
        self.lista_operacoes.heading('#1', text='Id')
        self.lista_operacoes.heading('#2', text='Cód.')
        self.lista_operacoes.heading('#3', text='Data')
        self.lista_operacoes.heading('#4', text='Qtd')
        self.lista_operacoes.heading('#5', text='Valor')
        self.lista_operacoes.heading('#6', text='Tipo Op.')
        self.lista_operacoes.heading('#7', text='Taxa')
        self.lista_operacoes.heading('#8', text='Tx. B3')
        self.lista_operacoes.heading('#9', text='Valor Op.')
        self.lista_operacoes.heading('#10', text='P. Med.')

        # a soma dos widths da lista com exceção do item 0, tem que dar 500
        self.lista_operacoes.column('#0', width=1)
        self.lista_operacoes.column('#1', width=20)
        self.lista_operacoes.column('#2', width=50)
        self.lista_operacoes.column('#3', width=75)
        self.lista_operacoes.column('#4', width=25)
        self.lista_operacoes.column('#5', width=50)
        self.lista_operacoes.column('#6', width=65)
        self.lista_operacoes.column('#7', width=30)
        self.lista_operacoes.column('#8', width=45)
        self.lista_operacoes.column('#9', width=80)
        self.lista_operacoes.column('#10', width=60)

        self.lista_operacoes.place(
            relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        # criação da barra de rolagem
        self.barra_rolagem = Scrollbar(self.frame_2, orient='vertical')
        self.lista_operacoes.configure(yscroll=self.barra_rolagem.set)
        self.barra_rolagem.place(
            relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

        self.lista_operacoes.bind('<Double-1>', self.duplo_clique)

    def menus(self):
        barra_menu = Menu(self.janela)
        self.janela.config(menu=barra_menu)
        menu_item1 = Menu(barra_menu)
        menu_item2 = Menu(barra_menu)
        menu_item3 = Menu(barra_menu)

        def sair(): self.janela.destroy()

        barra_menu.add_cascade(label='Opções', menu=menu_item1)
        barra_menu.add_cascade(label='Sobre', menu=menu_item2)
        # barra_menu.add_cascade(label='Relatórios', menu=menu_item2)

        menu_item1.add_command(label='Sair', command=sair)
        menu_item1.add_command(label='Limpar Tela', command=self.limpar_tela)
        menu_item2.add_command(label='Sobre a Versão')
        # menu_item2.add_command(label='Ficha da Operação', command=self.relatorio_operacao)

    def janela_calendario(self):
        self.janela_cal = Toplevel()
        self.janela_cal.title('Inserir data')
        self.janela_cal.configure(background='gray75')
        self.janela_cal.geometry('400x400')
        self.janela_cal.resizable(False, False)
        self.janela_cal.transient(self.janela)
        self.janela_cal.focus_force()
        self.janela_cal.grab_set()

aplicativo()