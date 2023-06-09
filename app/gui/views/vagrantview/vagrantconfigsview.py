import customtkinter as ctk
from argumentparser.helper import get_local_vagrant_boxes
from gui.widgets.projectnamewidget import VagrantProjectNameWidget
from gui.widgets.titlewidget import TitleWidget
from gui.widgets.vagrantboxsetupwidget import VagrantBoxSetUpWidget
from gui.widgets.vboxconfigswidget import VboxConfigsWidget
from gui.widgets.buttonswidget.vagrantmainbuttonswidget import VagrantMainButtons
from tkinter import StringVar


class VagrantConfigsView(ctk.CTkFrame):
    def __init__(self, master, provisions_configs):
        self.frame_name = 'configs'
        self.master = master
        self.provisions_configs = provisions_configs
        self.local_vagrant_boxes = get_local_vagrant_boxes()

        ctk.CTkFrame.__init__(self, master)
        family = 'Sans'
        self.title_std = ctk.CTkFont(
            family=family,
            size=30,
            weight='bold'
        )
        self.warning_font = ctk.CTkFont(family=family, size=11)
        self.font_std = ctk.CTkFont(family=family, size=18)
        self.set_grid()
        self.set_std_dimensions()
        self.add_titles()
        self.add_project_name()
        self.add_vagrant_box_setup()
        self.add_vbox_configs()
        self.add_connection_mode_frame()
        self.add_main_buttons()
        self.render()

    def set_std_dimensions(self):
        self.padx_std = (20, 20)
        self.pady_std = (10, 10)
        self.pady_title = (10, 2)
        self.pady_entry = (2, 10)
        self.ipadx_std = 10
        self.ipady_std = 10
        self.ipadx_button = 5
        self.ipady_button = 5
        self.sticky_title = 'wn'
        self.sticky_label = 'ws'
        self.sticky_entry = 'wn'
        self.sticky_up = 'wen'
        self.sticky_frame = 'wens'
        self.sticky_optionmenu = 'w'
        self.sticky_warningmsg = 'e'
        self.sticky_horizontal = 'ew'

    def set_grid(self):
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=0)

    def set_general_row_col_conf(self, frame: ctk.CTkFrame, rows: int, columns: int):
        # self.grid()
        for i in range(columns):
            frame.columnconfigure(i, weight=1)

        for i in range(rows):
            frame.rowconfigure(i, weight=1)

    def add_titles(self):
        self.title_frame = TitleWidget(
            master=self,
            title='Vagrant',
            subtitle='Configurations'
        )

    def add_project_name(self):
        self.project_name_frame = VagrantProjectNameWidget(
            master=self,
            provisions_configs=self.provisions_configs
        )

    def add_vagrant_box_setup(self):
        self.vagrant_box_setup_frame = VagrantBoxSetUpWidget(
            master=self,
            provisions_configs=self.provisions_configs
        )

    def add_vbox_configs(self):
        self.vbox_configs_frame = VboxConfigsWidget(
            master=self,
            provisions_configs=self.provisions_configs
        )

    def add_connection_mode_frame(self):
        self.connection_mode_frame = ctk.CTkFrame(self)
        self.connection_mode_frame.columnconfigure(0, weight=1)
        self.connection_mode_frame.columnconfigure(1, weight=1)
        self.connection_mode_frame.columnconfigure(2, weight=1)
        self.set_general_row_col_conf(
            frame=self.connection_mode_frame,
            rows=2,
            columns=1
        )

        ssh_label = ctk.CTkLabel(
            master=self.connection_mode_frame,
            text='Connection mode',
            font=self.font_std
        )
        ssh_label.grid(
            row=0,
            column=0,
            padx=self.padx_std,
            pady=self.pady_std,
            sticky=self.sticky_label,
        )

        self.connection_mode_var = StringVar()
        self.connection_mode_var.set('key')
        if self.provisions_configs["configurations"]["connection"]["default"]:
            self.connection_mode_var.set(
                self.provisions_configs["configurations"]["connection"]["default"]
            )

        ssh_key = ctk.CTkRadioButton(
            master=self.connection_mode_frame,
            text="ssh_key",
            font=self.font_std,
            value='key',
            variable=self.connection_mode_var,
            command=self.set_connection_mode
        )
        ssh_key.grid(
            row=0,
            column=1,
            padx=self.padx_std,
            pady=self.pady_std,
            sticky=self.sticky_label
        )

        password = ctk.CTkRadioButton(
            master=self.connection_mode_frame,
            text="password",
            value='password',
            font=self.font_std,
            variable=self.connection_mode_var,
            command=self.set_connection_mode
        )
        password.grid(
            row=0,
            column=2,
            padx=self.padx_std,
            pady=self.pady_std,
            sticky=self.sticky_label
        )

    def add_main_buttons(self):
        self.main_button_frame = VagrantMainButtons(
            master=self,
            provisions_configs=self.provisions_configs,
            wanted_buttons=['provisions', 'networks']
        )

    def render(self):
        self.title_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std,
            sticky=self.sticky_frame
        )
        self.project_name_frame.grid(
            row=1,
            column=0,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky=self.sticky_frame
        )
        self.vagrant_box_setup_frame.grid(
            row=2,
            column=0,
            rowspan=2,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky=self.sticky_frame,
        )
        self.vbox_configs_frame.grid(
            row=1,
            column=1,
            rowspan=3,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky=self.sticky_frame
        )
        self.connection_mode_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky=self.sticky_frame
        )
        self.main_button_frame.grid(
            row=0,
            column=1,
            padx=self.padx_std,
            pady=self.pady_std,
            ipadx=self.ipadx_std,
            ipady=self.ipady_std,
            sticky='ne'
        )

    def get_vagrant_configs(self):
        return self.provisions_configs

    def set_connection_mode(self):
        self.provisions_configs["configurations"]["connection"]["default"] = self.connection_mode_var.get()
