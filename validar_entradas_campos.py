from modulos import *

class validadores:
    def validar_campo(self, info):
        if info == '':
            return True
        try:
            valor = float(info)
        except ValueError:
            return False
        return valor