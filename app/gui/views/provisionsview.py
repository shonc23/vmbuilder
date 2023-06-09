import abc
import customtkinter as ctk
from gui.guistandard import GuiStandard
from gui.widgets.additionalscriptwidget import AdditionalScriptWidget
from gui.widgets.packermanager.mainpackagewidget import MainPackageWidget
from gui.widgets.titlewidget import TitleWidget


class ProvisionsFrame(GuiStandard):

    def __init__(self, master, provisions_configs, title):
        self.provisions_configs = provisions_configs
        self.title = title
        ctk.CTkFrame.__init__(self, master)
        self.set_fonts()
        self.set_std_dimensions()
        self.initialize_elements()
        self.render_elements()

    def set_fonts(self):
        family = 'Sans'
        self.title_std = ctk.CTkFont(
            family=family,
            size=30,
            weight='bold'
        )
        self.little_title = ctk.CTkFont(
            family=family,
            size=20,
            weight='bold'
        )
        self.font_std = ctk.CTkFont(family=family, size=18)

    def set_std_dimensions(self):
        self.padx_std = (20, 20)
        self.pady_std = (10, 10)
        self.pady_title = (10, 2)
        self.pady_entry = (2, 10)
        self.pad_left = (10, 5)
        self.pad_right = (5, 10)
        self.pad_equal = (5, 5)
        self.ipadx_std = 10
        self.ipady_std = 10
        self.ipadx_button = 5
        self.ipady_button = 5
        self.entry_height_std = 50
        self.width_button_std = 30
        self.padx_btn_right = (0, 5)
        self.padx_btn_left = (5, 0)
        self.sticky_title = 'wn'
        self.sticky_label = 'ws'
        self.sticky_entry = 'wn'
        self.sticky_frame = 'wens'
        self.sticky_optionmenu = 'w'
        self.sticky_warningmsg = 'e'
        self.sticky_horizontal = 'ew'

    def initialize_elements(self):
        self.title_frame = TitleWidget(
            self,
            title=self.title,
            subtitle='Provisions'
        )
        self.package_manager_frame = MainPackageWidget(
            self,
            self.provisions_configs
        )
        self.additional_scripts_frame = AdditionalScriptWidget(
            self,
            self.provisions_configs
        )
        self._initialize_main_buttons_frame()

    def render_elements(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.title_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std,
            sticky=self.sticky_frame,
        )
        self.package_manager_frame.grid(
            row=1,
            column=0,
            rowspan=3,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky=self.sticky_frame,
        )
        self.additional_scripts_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky=self.sticky_frame,
        )
        self.main_buttons_frame.grid(
            row=0,
            column=1,
            sticky=self.sticky_frame,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
        )

    @abc.abstractmethod
    def _initialize_main_buttons_frame(self):
        self.main_buttons_frame = ctk.CTkFrame()
