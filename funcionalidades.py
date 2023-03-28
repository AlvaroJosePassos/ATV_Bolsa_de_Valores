from modulos import *


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
        quantidade = int(list(self.cursor.execute(
            f"SELECT COUNT(codigo_operacao) AS quantidade FROM operacoes WHERE codigo_operacao = '{self.entrada_codigo_ativo.get()}' AND tipo_operacao = 'COMPRA';"))[0][0])
        if quantidade == 0:
            self.desconectar_banco()
            if self.entrada_tipo_operacao.get() == "COMPRA":
                return round(float(self.calculo_operacao())/float(self.entrada_qtd_acoes.get()), 2)
            return 0
        tupla_quantidade_do_ativo_compra = list(self.cursor.execute(
            f"SELECT SUM(qtd_acoes) FROM operacoes GROUP BY id_operacao HAVING codigo_operacao = '{self.entrada_codigo_ativo.get()}' AND tipo_operacao = 'COMPRA' ;"))
        tupla_preco_total_do_ativo_compra = list(self.cursor.execute(
            f"SELECT SUM(valor_operacao) FROM operacoes GROUP BY id_operacao HAVING codigo_operacao = '{self.entrada_codigo_ativo.get()}' AND tipo_operacao = 'COMPRA' ;"))
        print(tupla_preco_total_do_ativo_compra)
        print(tupla_quantidade_do_ativo_compra)
        quantidade_do_ativo_compra = 0
        preco_total_do_ativo_compra = 0
        for i in range(len(tupla_quantidade_do_ativo_compra)):
            quantidade_do_ativo_compra += float(
                tupla_quantidade_do_ativo_compra[i][0])
        quantidade_do_ativo_compra += float(self.entrada_qtd_acoes.get())
        for j in range(len(tupla_preco_total_do_ativo_compra)):
            preco_total_do_ativo_compra += float(
                tupla_preco_total_do_ativo_compra[j][0])
        preco_total_do_ativo_compra += float(self.calculo_operacao())
        print(preco_total_do_ativo_compra)
        print(quantidade_do_ativo_compra)
        if self.entrada_tipo_operacao.get() == "COMPRA":
            self.desconectar_banco()
            return round(preco_total_do_ativo_compra/quantidade_do_ativo_compra, 2)
        preco_ant = float(list(self.cursor.execute(
            f"SELECT preco_medio FROM operacoes GROUP BY id_operacao HAVING codigo_operacao = '{self.entrada_codigo_ativo.get()}' AND tipo_operacao = 'COMPRA' ;"))[-1][0])
        self.desconectar_banco()
        return preco_ant

    def limpar_tela(self):
        self.entrada_data.config(state='normal')
        self.entrada_id_operacao.delete(0, END)
        self.entrada_data.delete(0, END)
        self.entrada_qtd_acoes.delete(0, END)
        self.entrada_valor_unitario.delete(0, END)
        self.entrada_taxa_corretagem.delete(0, END)
        self.entrada_data.config(state='disable')

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
        if self.entrada_qtd_acoes.get() == "" or self.entrada_valor_unitario.get() == "" or self.entrada_data.get() == "" or self.entrada_taxa_corretagem.get() == "":
            mensagem = 'Para cadastrar uma operação, preencha todos os campos obrigatórios!'
            messagebox.showinfo('Informação de Erro', mensagem)
        else:
            self.variaveis()
            self.conectar_banco()
            self.cursor.execute('''INSERT INTO operacoes(codigo_operacao, data, qtd_acoes, valor_unitario, tipo_operacao, taxa_corretagem, taxa_b3, valor_operacao, preco_medio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.cod_ativo, self.data, self.qtd, self.valor_unt, self.tipo_op, self.taxa_corr, self.tx_b3, self.valor_op, self.preco_medio))
            self.conector.commit()
            self.label_preco_medio_atual.config(
                text=f'Ultimo Preço Medio Adicionado: {self.preco_medio}')
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
            self.entrada_data.config(state='normal')
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = self.lista_operacoes.item(
                termo, 'values')
            self.entrada_id_operacao.insert(END, col1)
            self.entrada_codigo_ativo.set(col2)
            self.entrada_data.insert(END, col3)
            self.entrada_qtd_acoes.insert(END, col4)
            self.entrada_valor_unitario.insert(END, col5)
            self.entrada_tipo_operacao.set(col6)
            self.entrada_taxa_corretagem.insert(END, col7)
            self.entrada_data.config(state='disable')

    def apagar_operacao(self):
        if self.entrada_qtd_acoes.get() == "" or self.entrada_valor_unitario.get() == "" or self.entrada_data.get() == "" or self.entrada_taxa_corretagem.get() == "":
            mensagem = 'Para apagar uma operação, selecione uma operação!'
            messagebox.showinfo('Informação de Erro', mensagem)
        else:
            self.variaveis()
            self.conectar_banco()
            self.conector.execute(
                '''DELETE FROM operacoes WHERE id_operacao = ?''', (self.id_oper, ))
            self.conector.commit()
            self.desconectar_banco()
            self.limpar_tela()
            self.select_lista()

    def alterar_operacao(self):
        if self.entrada_qtd_acoes.get() == "" or self.entrada_valor_unitario.get() == "" or self.entrada_data.get() == "" or self.entrada_taxa_corretagem.get() == "":
            mensagem = 'Para alterar uma operação, selecione uma operação!'
            messagebox.showinfo('Informação de Erro', mensagem)
        else:
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
        self.calendario = Calendar(self.aba1, fg='gray75', bg='blue', font=(
            'verdana', 8, 'bold'), locale='pt_br')
        self.calendario.place(relx=0.5, rely=0.1)
        self.gravar_data = Button(self.aba1, text='Inserir data', bd=2, bg='red', fg='white', font=(
            'verdana', 8, 'bold'), command=self.imprimir_data)
        self.gravar_data.place(relx=0.26, rely=0.64, relheight=0.10)

    def imprimir_data(self):
        data = self.calendario.get_date()
        self.calendario.destroy()
        self.entrada_data.config(state='normal')
        self.entrada_data.delete(0, END)
        self.entrada_data.insert(END, data)
        self.gravar_data.destroy()
        self.entrada_data.config(state='disable')
