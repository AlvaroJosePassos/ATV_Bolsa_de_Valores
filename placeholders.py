from modulos import *

class entrada_placeholder(Entry):
    def __init__(self, master = None, placeholder = 'PLACEHOLDER', color = 'gray'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.fg_padrao = self['fg']

        self.bind('<FocusIn>', self.foco_dentro)
        self.bind('<FocusOut>', self.foco_fora)

        self.inserir_placeholder()

    def inserir_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foco_dentro(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.fg_padrao

    def foco_fora(self, *args):
        if not self.get():
            self.inserir_placeholder()