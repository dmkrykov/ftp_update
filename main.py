from config import Config
from gui import Gui

if __name__ == '__main__':
    cfg = Config()
    gui = Gui(cfg)
    gui.window.mainloop()
