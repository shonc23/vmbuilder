import constants
import os
import customtkinter as ctk
from argumentparser.helper import get_local_vagrant_boxes
from existencecontroller.controller import launch_vboxmanage_lst_command
from gui.views.errors.errorview import ErrorMessage
from tkinter import ttk
from tkinter import StringVar


class VagrantConfigsView(ctk.CTkFrame):
    def __init__(self, master, provisions_configs):
        self.provisions_configs = provisions_configs
        ctk.CTkFrame.__init__(self, master)
        self.set_grid()

        title_font = ctk.CTkFont(
            family='DejaVu Sans',
            size=22,
            weight='bold'
        )
        little_title_font = ctk.CTkFont(
            family='DejaVu Sans',
            size=16,
        )

        # Add titles
        self.vagrant_label = ctk.CTkLabel(self, text="Vagrant", font=title_font)
        self.vagrant_label.grid(row=0, column=0, columnspan=4)

        self.conf_label = ctk.CTkLabel(self, text="Configurations", font=little_title_font)
        self.conf_label.grid(row=1, column=0, columnspan=4)

        separator = ttk.Separator(
            master=self,
            orient='horizontal',
            style='blue.TSeparator',
            class_=ttk.Separator,
            takefocus=1,
            cursor='plus'
        )
        separator.grid(row=2, column=0, columnspan=4, sticky='EW')

        # start form to get new machine configurations
        self.startcolumn = 1
        self.add_project_frame()
        self.add_vbox_hostname()
        self.add_credentials_frame()
        self.add_select_vagrant_box()
        self.add_connection_mode_frame()

    def add_project_frame(self):
        project_frame = ctk.CTkFrame(self)
        project_frame.grid(row=3, column=self.startcolumn, columnspan=2)
        project_frame.columnconfigure(0, weight=1)
        project_frame.columnconfigure(1, weight=1)
        project_frame.rowconfigure(0, weight=1)
        project_frame.rowconfigure(1, weight=1)
        machine_name_label = ctk.CTkLabel(project_frame, text="New project name:")
        machine_name_label.grid(row=0, column=0, columnspan=2)
        self.entry_project_name = ctk.CTkEntry(project_frame)
        self.entry_project_name.insert(
            0,
            self.provisions_configs["configurations"]["project_name"]
        )
        self.entry_project_name.grid(row=1, column=0, columnspan=2,
                                     padx=(10, 10), pady=(10, 10))

    def add_vbox_hostname(self):
        vbox_hostname_frame = ctk.CTkFrame(self)
        vbox_hostname_frame.grid(row=5, column=self.startcolumn, columnspan=2)
        vbox_hostname_frame.columnconfigure(0, weight=1)
        vbox_hostname_frame.columnconfigure(1, weight=1)
        vbox_hostname_frame.rowconfigure(0, weight=1)
        vbox_hostname_frame.rowconfigure(1, weight=1)
        vbox_name_label = ctk.CTkLabel(vbox_hostname_frame, text="Virtual box name:")
        vbox_name_label.grid(row=0, column=0)
        self.entry_vbox_name = ctk.CTkEntry(vbox_hostname_frame)
        self.entry_vbox_name.insert(
            0,
            self.provisions_configs["configurations"]['vbox_name']
        )
        self.entry_vbox_name.grid(row=1, column=0,
                                  padx=(10, 10), pady=(10, 10))

        hostname_label = ctk.CTkLabel(vbox_hostname_frame, text="Hostname:")
        hostname_label.grid(row=0, column=1)
        self.entry_hostname = ctk.CTkEntry(vbox_hostname_frame)
        self.entry_hostname.insert(
            0,
            self.provisions_configs["configurations"]['hostname']
        )
        self.entry_hostname.grid(row=1, column=1,
                                 padx=(10, 10), pady=(10, 10))

    def add_credentials_frame(self):
        credentials_frame = ctk.CTkFrame(self)
        credentials_frame.grid(row=7, column=self.startcolumn, columnspan=2)
        credentials_frame.columnconfigure(0, weight=1)
        credentials_frame.columnconfigure(1, weight=1)
        credentials_frame.rowconfigure(0, weight=1)
        credentials_frame.rowconfigure(1, weight=1)
        credentials_frame.rowconfigure(2, weight=1)
        credentials_frame.rowconfigure(3, weight=1)
        username_label = ctk.CTkLabel(credentials_frame, text="Username:")
        username_label.grid(row=0, column=0)
        self.entry_default_username = ctk.CTkEntry(credentials_frame)
        self.entry_default_username.insert(
            0,
            self.provisions_configs["credentials"]['username']
        )
        self.entry_default_username.grid(row=1, column=0,
                                         padx=(10, 10), pady=(10, 10))

        machine_name_label = ctk.CTkLabel(credentials_frame, text="Password:")
        machine_name_label.grid(row=0, column=1)
        self.entry_default_password = ctk.CTkEntry(credentials_frame)
        self.entry_default_password.insert(
            0,
            self.provisions_configs["credentials"]['password']
        )
        self.entry_default_password.grid(row=1, column=1,
                                         padx=(10, 10), pady=(10, 10))

        machine_name_label = ctk.CTkLabel(credentials_frame, text="Extra user:")
        machine_name_label.grid(row=2, column=0, columnspan=2)
        self.entry_extra_user = ctk.CTkEntry(credentials_frame)
        self.entry_extra_user.insert(
            0,
            self.provisions_configs["credentials"]['extra_user']
        )
        self.entry_extra_user.grid(row=3, column=0, columnspan=2,
                                   padx=(10, 10), pady=(10, 10))

    def add_select_vagrant_box(self):
        # Select vagrant boxes.
        # If there are no vagran boxes an entry is displayed,
        # otherwise an optionmenu will appear
        if get_local_vagrant_boxes() == 'No Box':
            no_box_frame = ctk.CTkFrame(
                self,
            )
            no_box_frame.grid(row=12, column=self.startcolumn, columnspan=2)
            no_box_frame.columnconfigure(0, weight=1)
            no_box_frame.rowconfigure(0, weight=1)
            no_box_frame.rowconfigure(1, weight=1)
            vagrant_box_name_label = ctk.CTkLabel(
                no_box_frame,
                text=(
                    'You do not have local Vagrant box.\n'
                    'Insert cloud Vagrant box name:'
                )
            )
            vagrant_box_name_label.grid(row=0, column=0)
            self.vagrant_box = ctk.CTkEntry(no_box_frame)
            self.vagrant_box.insert(
                0,
                self.provisions_configs["configurations"]["image"]
            )
            self.vagrant_box.grid(row=1, column=0,
                                  padx=(10, 10), pady=(10, 10))
        else:
            self.vagrant_box = ctk.StringVar(self)
            self.vagrant_box.set('Select Vagrant Box')
            vagrant_drop = ctk.CTkOptionMenu(
                master=self,
                variable=self.vagrant_box,
                values=get_local_vagrant_boxes().split("\n"),
            )
            vagrant_drop.grid(row=11, column=self.startcolumn, sticky="ew", columnspan=2)

    def add_connection_mode_frame(self):
        connection_mode_frame = ctk.CTkFrame(self)
        connection_mode_frame.grid(row=13, column=self.startcolumn, columnspan=2, rowspan=2,
                                   padx=(10, 10), pady=(10, 10))
        connection_mode_frame.columnconfigure(0, weight=1)
        connection_mode_frame.columnconfigure(1, weight=1)
        connection_mode_frame.rowconfigure(0, weight=1)
        connection_mode_frame.rowconfigure(1, weight=1)

        ssh_label = ctk.CTkLabel(connection_mode_frame, text='Connection mode')
        ssh_label.grid(row=0, column=0, columnspan=2)
        self.connection_mode_var = StringVar()
        if self.provisions_configs["configurations"]["connection"] == 'key':
            self.connection_mode_var.set('key')
        elif self.provisions_configs["configurations"]["connection"] == 'password':
            self.connection_mode_var.set('password')
        ssh_key = ctk.CTkRadioButton(
            connection_mode_frame,
            text="ssh_key",
            variable=self.connection_mode_var,
            value='key'
        )
        ssh_key.grid(row=1, column=0, padx=(10, 10), pady=(10, 10))
        password = ctk.CTkRadioButton(
            connection_mode_frame,
            text="password",
            variable=self.connection_mode_var,
            value='password',
            command=self.set_connection_mode
        )
        password.grid(row=1, column=1, padx=(10, 10), pady=(10, 10))

        save_button = ctk.CTkButton(
            self,
            text='Set Provisions',
            command=self.go_to_provision_page
        )
        save_button.grid(row=15, column=self.startcolumn, columnspan=2)

    def set_grid(self):
        self.grid()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # title row
        self.rowconfigure(0, weight=2)
        # config row
        self.rowconfigure(1, weight=2)
        # separator row
        self.rowconfigure(2, weight=1)
        # label name
        self.rowconfigure(3, weight=1)
        # entry name
        self.rowconfigure(4, weight=1)
        # vbox label, hostname label
        self.rowconfigure(5, weight=1)
        # vbox entry, hostname entry
        self.rowconfigure(6, weight=1)
        # username label, password label
        self.rowconfigure(7, weight=1)
        # username entry, password entry
        self.rowconfigure(8, weight=2)
        # extra user label
        self.rowconfigure(9, weight=2)
        # extra user entry
        self.rowconfigure(10, weight=2)
        # select vagrant box
        self.rowconfigure(11, weight=2)
        # optional entry name for vagrant box
        self.rowconfigure(12, weight=2)
        # select connection mode label
        self.rowconfigure(13, weight=2)
        # radiobuttons connection mode
        self.rowconfigure(14, weight=2)
        # back, next buttons
        self.rowconfigure(15, weight=2)

    def go_to_provision_page(self):
        project_name = self.entry_project_name.get()
        if project_name in os.listdir(constants.VAGRANT_MACHINES_PATH):
            ErrorMessage(self, 'A machine with this name already exists')
        elif not project_name:
            ErrorMessage(self, 'You must choose a name for the virtual machine')
        elif not self.entry_vbox_name.get():
            ErrorMessage(self, 'You must choose a name for the virtual box machine')
        elif self.entry_vbox_name.get() in launch_vboxmanage_lst_command():
            ErrorMessage(self, 'A box with the same name already exists')
        elif not self.entry_hostname.get():
            ErrorMessage(self, 'You must choose a hostname')
        elif not self.entry_default_username.get():
            ErrorMessage(self, 'You must choose a main username')
        elif not self.entry_default_password.get():
            ErrorMessage(self, 'You must choose a password')
        elif self.vagrant_box.get() == 'Select Vagrant Box':
            ErrorMessage(self, 'You must select a Vagrant box')
        else:
            self.provisions_configs["configurations"]["project_name"] = project_name
            self.provisions_configs["configurations"]["vbox_name"] = self.entry_vbox_name.get()
            self.provisions_configs["configurations"]["hostname"] = self.entry_hostname.get()
            self.provisions_configs["credentials"]["username"] = self.entry_default_username.get()
            self.provisions_configs["credentials"]["password"] = self.entry_default_password.get()
            self.provisions_configs["credentials"]["extra_user"] = self.entry_extra_user.get()
            self.provisions_configs["configurations"]["image"] = self.vagrant_box.get()
            self.destroy()
            self.master.add_vagrant_provisions_frame()

    def get_vagrant_configs(self):
        return self.provisions_configs

    def set_connection_mode(self):
        self.provisions_configs["configurations"]["connection"] = self.connection_mode_var.get()
