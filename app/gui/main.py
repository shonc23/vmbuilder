import constants
import customtkinter as ctk
import json
import os
from gui.views.vagrantview.vagrantconfigsview import VagrantConfigsView
from gui.views.vagrantview.vagrantprovisionspackagesview import VagrantProvisionsPackagesView
from gui.views.vagrantview.vagrantprovisionsscriptview import VagrantProvisionsScriptView


dir_path = os.path.dirname(os.path.realpath(__file__))
# ctk.set_appearance_mode('dark')
ctk.set_default_color_theme(f'{dir_path}/views/dark_blue.json')


class MainView(ctk.CTkFrame):

    def __init__(self, master):
        ctk.CTkFrame.__init__(self, master)
        self.master = master
        self.rows = 4
        self.columns = 3
        self.set_grid(rows=self.rows, columns=self.columns)
        self.add_machines_types_button()
        self.add_bottom_button()
        self.pack(side="top", fill="both", expand=True)

    def add_machines_types_button(self):
        self.types_frame = ctk.CTkFrame(self)
        self.types_frame.grid(row=0, column=0, columnspan=self.columns)
        vagrant_button = ctk.CTkButton(self.types_frame, text='Vagrant',
                                       command=self.add_vagrant_configs)
        vagrant_button.pack(side='left', padx=(10, 100), pady=10)

        packer_button = ctk.CTkButton(self.types_frame, text='Packer',
                                      command=self.add_packer_configs)
        packer_button.pack(side='right', padx=(100, 10), pady=10)

    def add_bottom_button(self, back: bool = False):
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=self.rows-1, column=0, columnspan=3)
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.columnconfigure(2, weight=1)
        self.bottom_frame.columnconfigure(3, weight=1)
        self.bottom_frame.rowconfigure(0, weight=1)
        if not back:
            exit_button = ctk.CTkButton(self.bottom_frame, text='exit',
                                        command=self.close_window)
            exit_button.grid(row=0, column=1, columnspan=2)
        else:
            exit_button = ctk.CTkButton(self.bottom_frame, text='exit',
                                        command=self.close_window)
            exit_button.grid(row=0, column=2)
            back_button = ctk.CTkButton(self.bottom_frame, text='Back',
                                        command=lambda args=(self, back): start(*args))
            back_button.grid(row=0, column=1)

    def set_grid(self, rows: int, columns: int):
        self.grid()
        for i in range(columns):
            self.columnconfigure(i, weight=1)

        for i in range(rows):
            self.rowconfigure(i, weight=1)

    def add_vagrant_configs(self):
        with open(f'{constants.VAGRANT_PROVS_CONFS_PATH}/template.json') as template_json:
            self.provisions_configs = json.loads(template_json.read())
        for operation in ('install', 'uninstall', 'config'):
            self.provisions_configs["provisions"][f"packages_to_{operation}"] = set()
        vagrant_configs_view = VagrantConfigsView(
            master=self,
            provisions_configs=self.provisions_configs
        )
        vagrant_configs_view.grid(row=1, column=1, rowspan=2,
                                  sticky='wens')
        self.add_bottom_button(back=True)
        self.types_frame.destroy()

    def add_vagrant_provisions_frame(self):
        vagrant_configs_view = VagrantProvisionsScriptView(
            master=self,
            provisions_configs=self.provisions_configs
        )
        vagrant_configs_view.grid(row=1, column=0, columnspan=3, sticky='wens')
        vagrant_configs_view = VagrantProvisionsPackagesView(
            master=self,
            provisions_configs=self.provisions_configs
        )
        vagrant_configs_view.grid(row=2, column=0, columnspan=5, sticky='wens')

    def add_packer_configs(self):
        pass

    def close_window(self):
        self.master.destroy()


def start(mainview=None, back=False):
    if back:
        mainview.master.destroy()
    root = ctk.CTk()
    root.wm_geometry("800x1000")
    main = MainView(root)
    main.master.title('HackTheMonkey')
    root.mainloop()


if __name__ == "__main__":
    start()
