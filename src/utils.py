import sys
import os

def resource_path(relative_path):
    """
    Retorna o caminho absoluto para recursos, considerando se o script foi
    empacotado com PyInstaller ou não.
    """
    try:
        # Quando empacotado pelo PyInstaller
        base_path = sys._MEIPASS
    except AttributeError:
        # Quando executado como script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
