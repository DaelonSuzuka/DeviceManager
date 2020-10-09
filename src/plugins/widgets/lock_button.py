from qt import *
import qtawesome as qta
from style import qcolors


class LockButton(ConfirmToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setToolTip('Lock Power Output')
        self.icons = [
            qta.icon('fa.lock', color=qcolors.gray),
            qta.icon('fa.question-circle-o', color=qcolors.gray),
            qta.icon('fa.unlock-alt', color=qcolors.red)
        ]
        self.state = 0