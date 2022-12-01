from modulos import *

class validadores:
    def validar_campo(self, info):
        """--> função que faz a verificação de erro para n ser possível colocar caracteres diferentes de float"""
        if info == '':
            return True
        try:
            valor = float(info)
        except ValueError:
            return False
        return valor
