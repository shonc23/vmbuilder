from gui.views.provisionsview import ProvisionsFrame
from gui.widgets.buttonswidget.packermainbuttonswidget import PackerMainButtons


class PackerProvisionsView(ProvisionsFrame):

    def __init__(self, master, provisions_configs):
        self.frame_name = 'provisions'
        self.provisions_frame = super()
        self.provisions_frame.__init__(
            master=master,
            provisions_configs=provisions_configs,
            title='Packer'
        )

    def set_std_dimensions(self):
        self.provisions_frame.set_std_dimensions()

    def set_grid(self):
        self.provisions_frame.set_grid()

    def render(self):
        self.provisions_frame.render()

    def add_main_button_frame(self):
        self.main_buttons_frame = PackerMainButtons(
            master=self,
            provisions_configs=self.provisions_configs,
            wanted_buttons=['configs']
        )