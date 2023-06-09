import customtkinter as ctk
from existencecontroller.controller import launch_vboxmanage_lst_command
from gui.guistandard import GuiStandard


class VboxConfigsWidget(GuiStandard):

    def __init__(self, master, provisions_configs):
        self.provisions_configs = provisions_configs
        self.vbox_list = launch_vboxmanage_lst_command()
        ctk.CTkFrame.__init__(self, master)
        self.set_fonts()
        self.set_std_dimensions()
        self.initialize_elements()
        self.render_elements()

    def set_std_dimensions(self):
        self.padx_std = (20, 20)
        self.pady_std = (10, 10)
        self.pady_up = (10, 0)
        self.pady_down = (0, 10)
        self.pady_title = (10, 2)
        self.pady_entry = (2, 10)
        self.ipadx_std = 10
        self.ipady_std = 10
        self.entry_height_std = 40
        self.sticky_title = 'wn'
        self.sticky_label = 'w'
        self.sticky_entry = 'w'
        self.sticky_frame = 'wens'
        self.sticky_horizontal = 'we'

    def set_fonts(self):
        family = 'Sans'
        self.font_std = ctk.CTkFont(family=family, size=18)
        self.warning_font = ctk.CTkFont(family=family, size=11)

    def initialize_elements(self):
        self._intialize_subframes()
        self._initialize_vbox_subframe_elements()
        self._initialize_cpus_subframe_elements()
        self._initialize_memory_subframe_elements()
        self._initialize_disk_size_subframe_elements()

    def render_elements(self):
        self._render_vbox_subframe_elements()
        self._render_cpus_subframe_elements()
        self._render_memory_subframe_elements()
        self._render_disk_size_subframe_elements()
        self._render_subframes()

    def _intialize_subframes(self):
        self.vbox_subframe = ctk.CTkFrame(self)
        self.cpus_subframe = ctk.CTkFrame(self)
        self.memory_subframe = ctk.CTkFrame(self)
        self.disk_size_subframe = ctk.CTkFrame(self)

    def _initialize_vbox_subframe_elements(self):
        self.vbox_name_label = ctk.CTkLabel(
            master=self.vbox_subframe,
            text="Virtual box name:",
            font=self.font_std
        )
        self.vbox_name_entry = ctk.CTkEntry(
            master=self.vbox_subframe,
            font=self.font_std,
            height=self.entry_height_std,
            placeholder_text='Virtualbox name to be created'
        )
        if self.provisions_configs["configurations"]['vbox_name']["default"]:
            self.vbox_name_entry.insert(
                0,
                self.provisions_configs["configurations"]['vbox_name']["default"]
            )
        self.warning_label_vbox = ctk.CTkLabel(
            master=self.vbox_subframe,
            font=self.warning_font,
            text=""
        )
        self.vbox_name_entry.bind("<Configure>", self._vbox_name_check)
        self.vbox_name_entry.bind("<KeyRelease>", self._vbox_name_check)
        self.warning_label_vbox = ctk.CTkLabel(
            master=self.vbox_subframe,
            font=self.warning_font,
            text_color='red',
            text=""
        )
        if self.provisions_configs["configurations"]['vbox_name'] in self.vbox_list:
            self.warning_label_vbox.configure(
                text='A box with this name already exists',
            )

    def _initialize_cpus_subframe_elements(self):
        self.cpus_label = ctk.CTkLabel(
            master=self.cpus_subframe,
            font=self.font_std,
            text='Specify CPUs number'
        )
        self.cpus_value = ctk.IntVar()
        self.cpus_value.set(2)
        if self.provisions_configs["configurations"]["cpus"]["default"]:
            self.cpus_value.set(
                int(self.provisions_configs["configurations"]["cpus"]["default"])
            )
        self.cpus_slider = ctk.CTkSlider(
            master=self.cpus_subframe,
            variable=self.cpus_value,
            from_=1,
            to=8,
            number_of_steps=7,
            command=self._show_cpus_slider_value
        )
        self.cpus_slider_label = ctk.CTkLabel(
            master=self.cpus_subframe,
            text="",
            width=250
        )

    def _initialize_memory_subframe_elements(self):
        self.memory_label = ctk.CTkLabel(
            master=self.memory_subframe,
            font=self.font_std,
            text='Specify Memory in MB'
        )
        self.memory_var = ctk.IntVar()
        self.memory_var.set(8192)
        if self.provisions_configs["configurations"]["memory"]["default"]:
            self.memory_var.set(
                int(self.provisions_configs["configurations"]["memory"]["default"])
            )
        self.memory_slider = ctk.CTkSlider(
            master=self.memory_subframe,
            variable=self.memory_var,
            from_=2,
            to=16384,
            number_of_steps=8191,
            command=self._show_memory_slider_value
        )

        self.combo_value_memory = ctk.CTkComboBox(
            master=self.memory_subframe,
            variable=self.memory_var,
            font=self.font_std,
            values=["2", "4", "8", "16", "32", "64", "128", "256", "512",
                    "1024", "2048", "4096", "8192", "16384"],
            command=self._show_memory_slider_value
        )
        self.slider_memory_label = ctk.CTkLabel(
            self.memory_subframe,
            text="",
        )
        self.combo_value_memory.bind(
            '<KeyRelease>',
            self._show_memory_value_with_keyrelease
        )

    def _initialize_disk_size_subframe_elements(self):
        self.disk_label = ctk.CTkLabel(
            master=self.disk_size_subframe,
            font=self.font_std,
            text='Specify Disk Size in MB'
        )
        self.disk_slider_value = ctk.IntVar()
        self.disk_slider_value.set(30)
        self.disk_slider = ctk.CTkSlider(
            master=self.disk_size_subframe,
            variable=self.disk_slider_value,
            from_=4,
            to=2048,
            number_of_steps=2044,
            command=self._show_disk_size_value
        )
        self.disk_entry = ctk.CTkEntry(
            master=self.disk_size_subframe,
            font=self.font_std,
        )
        if self.provisions_configs["configurations"]["disk_size"]["default"]:
            self.disk_slider_value.set(
                int(self.provisions_configs["configurations"]["disk_size"]["default"])
            )
            self.disk_entry.insert(
                0,
                self.disk_slider_value.get()
            )
        self.disk_slider_label = ctk.CTkLabel(
            master=self.disk_size_subframe,
            text="",
            width=250
        )
        self.disk_entry.bind(
            '<KeyRelease>',
            self._show_disk_size_value_with_keyrelease
        )
        self.disk_slider.bind(
            '<Button-1>',
            self._set_disk_size_entry
        )
        self.disk_slider.bind(
            '<B1-Motion>',
            self._set_disk_size_entry
        )

    def _render_subframes(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.vbox_subframe.grid(
            row=0,
            column=0,
            sticky=self.sticky_frame,
            padx=self.padx_std,
            pady=self.pady_up
        )
        self.cpus_subframe.grid(
            row=1,
            column=0,
            sticky=self.sticky_frame,
            padx=self.padx_std,
            pady=self.pady_up
        )
        self.memory_subframe.grid(
            row=2,
            column=0,
            sticky=self.sticky_frame,
            padx=self.padx_std,
            pady=self.pady_up
        )
        self.disk_size_subframe.grid(
            row=3,
            column=0,
            sticky=self.sticky_frame,
            padx=self.padx_std,
            pady=self.pady_std
        )

    def _render_vbox_subframe_elements(self):
        self.vbox_subframe.columnconfigure(0, weight=1)
        self.vbox_subframe.rowconfigure(0, weight=1)
        self.vbox_subframe.rowconfigure(1, weight=1)
        self.vbox_subframe.rowconfigure(2, weight=1)
        self.vbox_name_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_title,
            sticky=self.sticky_label
        )
        self.vbox_name_entry.grid(
            row=1,
            column=0,
            padx=self.padx_std,
            pady=self.pady_entry,
            sticky=self.sticky_horizontal
        )
        self.warning_label_vbox.grid(
            row=2,
            column=0,
            padx=self.padx_std,
            pady=0,
            sticky=self.sticky_label
        )
        self.warning_label_vbox.grid(
            row=2,
            column=0,
            padx=self.padx_std,
            pady=0,
            sticky=self.sticky_label
        )

    def _render_cpus_subframe_elements(self):
        self.cpus_subframe.columnconfigure(0, weight=1)
        self.cpus_subframe.rowconfigure(0, weight=1)
        self.cpus_subframe.rowconfigure(1, weight=1)
        self.cpus_subframe.rowconfigure(2, weight=1)
        self.cpus_label.grid(
            row=0,
            column=0,
            sticky=self.sticky_label,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self.cpus_slider.grid(
            row=1,
            column=0,
            sticky=self.sticky_horizontal,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self.cpus_slider_label.grid(
            row=2,
            column=0,
            padx=self.padx_std,
            pady=self.pady_std
        )
        self._show_cpus_slider_value(self.cpus_slider.get())

    def _render_memory_subframe_elements(self):
        self.memory_subframe.columnconfigure(0, weight=1)
        self.memory_subframe.columnconfigure(1, weight=0)
        self.memory_subframe.rowconfigure(0, weight=1)
        self.memory_subframe.rowconfigure(1, weight=1)
        self.memory_subframe.rowconfigure(2, weight=1)
        self.memory_label.grid(
            row=0,
            column=0,
            sticky=self.sticky_label,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self.memory_slider.grid(
            row=1,
            column=0,
            sticky=self.sticky_horizontal,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self.combo_value_memory.grid(
            row=1,
            column=1,
            sticky=self.sticky_entry,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self._show_memory_slider_value(self.memory_slider.get())

    def _render_disk_size_subframe_elements(self):
        self.disk_size_subframe.columnconfigure(0, weight=1)
        self.disk_size_subframe.columnconfigure(1, weight=0)
        self.disk_size_subframe.rowconfigure(0, weight=1)
        self.disk_size_subframe.rowconfigure(1, weight=1)
        self.disk_size_subframe.rowconfigure(2, weight=1)
        self.disk_label.grid(
            row=0,
            column=0,
            sticky=self.sticky_label,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self.disk_slider.grid(
            row=1,
            column=0,
            sticky=self.sticky_horizontal,
            padx=self.padx_std,
            pady=self.pady_title
        )
        self.disk_entry.grid(
            row=1,
            column=1,
            padx=self.padx_std,
            pady=self.pady_entry,
            sticky=self.sticky_entry
        )
        self.disk_slider_label.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std
        )
        self.slider_memory_label.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=self.padx_std,
            pady=self.pady_std
        )
        self._show_disk_size_value(self.disk_slider_value.get())

    def _vbox_name_check(self, event):
        vbox_name_typed = self.vbox_name_entry.get()
        if vbox_name_typed not in self.vbox_list:
            self.vbox_name_entry.configure(border_color=["#979DA2", "#565B5E"])
            self.warning_label_vbox.configure(
                text='',
            )
        if vbox_name_typed in self.vbox_list:
            self.vbox_name_entry.configure(border_color='red')
            self.warning_label_vbox.configure(
                text='A virtualbox with this name already exists',
                text_color='red'
            )

    def _show_cpus_slider_value(self, cpus_value):
        if cpus_value:
            self.cpus_slider_label.configure(
                font=self.font_std,
                text=f'CPUs Selected: {int(cpus_value)}'
            )

    def _show_memory_slider_value(self, memory_value):
        if memory_value:
            self.slider_memory_label.configure(
                font=self.font_std,
                text=f'Selected Value: {int(self.memory_var.get())} MB'
            )

    def _show_memory_value_with_keyrelease(self, event):
        self._show_memory_slider_value(self.memory_var.get())

    def _show_disk_size_value(self, disk_value):
        if disk_value:
            value_text = f'{self.disk_slider_value.get()} MB'
            if self.disk_slider_value.get() >= 1024:
                disk_value = self.disk_slider_value.get() / 1_024
                value_text = f'{disk_value:.2f} GB'
            if disk_value >= 1024:
                disk_value = self.disk_slider_value.get() / 1_048_576
                value_text = f'{disk_value:.2f} TB'
            self.disk_slider_label.configure(
                font=self.font_std,
                text=f'Disk Size: {value_text}'
            )

    def _set_disk_size_entry(self, event):
        self.disk_entry.delete(0, 100)
        self.disk_entry.insert(0, self.disk_slider_value.get())

    def _show_disk_size_value_with_keyrelease(self, event):
        self.disk_slider_value.set(int(self.disk_entry.get()))
        self._show_disk_size_value(int(self.disk_entry.get()))
