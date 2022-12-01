from modulos import *

class validadores:
    def validar_campo(self, info):
        """--> função que faz a verificação de erro para não ser possível colocar caracteres diferentes de float em certos campos"""
        if info == '':
            return True
        try:
            valor = float(info)
        except ValueError:
            return False
        return valor
