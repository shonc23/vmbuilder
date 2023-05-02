import constants
import json
import logging
import os
import shutil
from builder.builder import Builder
from error import (
    FlagError,
    ExistenceProjectError,
    NoFileToUploadError
)
from helper import (
    convert_argv_list_to_dict,
    empty_script,
    PACKER_FLAGS_TO_ERROR,
)


class Packer(Builder):
    def __init__(self) -> None:
        self.arguments: dict = convert_argv_list_to_dict()
        self.machine_path: str = constants.vmbuilder_path + '/machines/packer'
        self.provisions_configs = constants.packer_provs_confs_path
        self.configs: dict = dict()
        self.provisions: dict = dict()

    def set_configs(self):
        config_provision_file_path = f'{self.provisions_configs}/{self.arguments["-j"]}'
        with open(config_provision_file_path, 'r') as provisions:
            configs = json.loads(provisions.read())["vbox-configs"]
        configs['iso_file'] = self.arguments['-if']
        configs['iso_link'] = self.arguments['-il']
        configs['iso_checksum'] = self.arguments['-cs']
        configs['vm_name'] = self.arguments['-vm']
        self.configs = configs.copy()

    def set_provisions(self):
        config_provision_file_path = f'{self.provisions_configs}/{self.arguments["-j"]}'
        with open(config_provision_file_path, 'r') as provisions:
            self.provisions = json.loads(provisions.read())["vbox-provisions"].copy()

    def check_flags(self):
        prompted_flags = set(self.arguments.keys())
        necessary_flags = set(PACKER_FLAGS_TO_ERROR.keys())
        forgotten_flags = set()

        # Check missing flags
        if not necessary_flags.issubset(prompted_flags):
            forgotten_flags = {
                flag for flag in necessary_flags if flag not in prompted_flags
            }

        # Check if some flags are written but without value
        for key in self.arguments:
            if not self.arguments[key]:
                forgotten_flags.add(key)

        if forgotten_flags:
            error_msg = '\n'
            for forgotten_flag in forgotten_flags:
                error_msg += f'\t\t{forgotten_flag}:\t{PACKER_FLAGS_TO_ERROR[forgotten_flag]}\n'
            raise FlagError(error_msg)

    def check_folder_vb_json_existence(self):
        if self.arguments['-n'] in os.listdir(self.machine_path):
            raise ExistenceProjectError("[ERROR] Project already exists!")

    def create_project_folder(self):
        project_folder = f'{self.machine_path}/{self.arguments["-n"]}'
        os.mkdir(project_folder)

        shutil.copytree(
            src=f'{constants.packer_http_path}/',
            dst=f'{project_folder}/http'
        )

    def _generate_packer_variable(self, variable: str):
        number = 30
        chars = len(variable)
        space = (number - chars) * ' '
        return f'  {variable}{space}= \"${{var.{variable}}}\"\n'

    def _generate_vars_file(self, json_file: dict):
        with open(f'{constants.packer_machines_path}/{self.arguments["-n"]}/vars.pkr.hcl', 'w') as vars_file:
            for var in json_file:
                if var in {'iso_file', 'iso_link', 'iso_checksum', 'vm_name'}:
                    json_file[var]["default"] = self.configs[var]
                if var == 'output_directory':
                    if not json_file[var]["default"]:
                        json_file[var]["default"] = constants.packer_builds_path
                if var == 'iso_directory':
                    if not json_file[var]["default"]:
                        json_file[var]["default"] = constants.iso_path
                if var == 'boot_command':
                    with open(f'{constants.packer_http_path}/boot_command.txt') as boot_command:
                        lines = boot_command.read()
                    json_file[var]["default"] = lines

                description = json_file[var]["description"]
                variable_value = json_file[var]["default"]
                if isinstance(variable_value, str):
                    variable_type = 'string'
                elif isinstance(variable_value, bool):
                    variable_type = 'bool'
                    variable_value = str(variable_value).lower()
                self.write_variable_directive(
                    variable_file=vars_file,
                    variable_name=var,
                    description=description,
                    variable_type=variable_type,
                    value=variable_value
                    )

    def _generate_main_file(self, json_file: dict):
        with open(f'{constants.packer_machines_path}/{self.arguments["-n"]}/main.pkr.hcl', 'w') as main_file:
            main_file.write(
                'locals {\n'
                f'{self._generate_packer_variable("output_directory")}'
                '}\n\n'
            )
            main_file.write('source "virtualbox-iso" "vbox" {\n')
            for var in json_file['vbox-configs']:
                space = (30 - len(var)) * ' '
                if var in ['start_retry_timeout', 'iso_file']:
                    continue
                elif var == 'boot_command':
                    main_file.write(f'  {var}{space}= [ var.{var} ]\n')
                elif var == 'iso_directory':
                    main_file.write(
                        '  iso_target_path               = "${var.iso_directory'
                        '}/${var.iso_file' + '}"\n'
                    )
                elif var == 'iso_link':
                    main_file.write(
                        '  iso_urls = [\n'
                        '    "${var.output_directory' + '}/${var.iso_file' + '}",\n'
                        '    "${var.iso_link' + '}",\n'
                        '  ]\n'
                    )
                elif var == 'ssh_password':
                    main_file.write(
                        f'  shutdown_command              = "echo ' + "'" 
                        '${var.ssh_password' + '}' + "'" + ' | sudo -E -S poweroff"\n'
                    )
                    main_file.write(self._generate_packer_variable(var))
                else:
                    main_file.write(self._generate_packer_variable(var))
            main_file.write(
                '  vboxmanage = [\n'
                '    ["modifyvm", "' + '{' + '{' + ' .Name ' + '}' + '}", "--rtcuseutc", "off"],\n'
                '    ["modifyvm", "' + '{' + '{' + ' .Name ' + '}' + '}", "--vram", "128"]\n'
                '  ]\n'
                '  virtualbox_version_file       = "/tmp/.vbox_version"\n'
            )
            main_file.write('}\n\n')

            main_file.write(
                'build {\n\n'
                '  sources = ["source.virtualbox-iso.vbox"]\n\n'
            )

            scripts = list()
            programs = json_file['vbox-provisions']['programs']
            custom_scripts = json_file['vbox-provisions']['custom-scripts']
            upload = json_file['vbox-provisions']['upload']
            files_to_upload_from_json = json_file['vbox-provisions']['files_to_upload']

            if programs['update-upgrade']:
                script = f'{constants.bash_path}/update-upgrade.sh'
                scripts.append(script)
            if programs['update-upgrade-full']:
                script = f'{constants.bash_path}/update-upgrade-full.sh'
                scripts.append(script)
            if programs['install']:
                for program in programs['install']:
                    script = f'{constants.programs_path}/{program}/install.sh'
                    scripts.append(script)
                    config_file = f'{constants.programs_path}/{program}/configs/config.sh'
                    script_is_empty, _ = empty_script(config_file)
                    if not script_is_empty:
                        scripts.append(script)

            if programs['uninstall']:
                for program in programs['uninstall']:
                    script = f'{constants.programs_path}/{program}/uninstall.sh'
                    scripts.append(script)
            if programs['clean']:
                script = f'{constants.bash_path}/clean.sh'
                scripts.append(script)

            if upload:
                script = f'{constants.bash_path}/prepare-for-upload.sh'
                scripts.append(script)

            self.provisioner_shell(scripts=scripts, main_file=main_file)

            if upload and files_to_upload_from_json:
                files_to_upload = [f"{constants.upload_path}/{file}" for file in files_to_upload_from_json]
                self.provisioner_file(files=files_to_upload, main_file=main_file)
            if upload and not files_to_upload:
                print("warning! there are no files specified to upload!")

            if custom_scripts:
                custom_scripts = [f'{constants.custom_scripts_path}/{script}' for script in custom_scripts]
                self.provisioner_shell(scripts=custom_scripts, main_file=main_file)
                files_to_upload_from_scripts = list()
                for custom_script in custom_scripts:
                    with open(custom_script, 'r') as script_file:
                        lines = script_file.readlines()
                    for line in lines:
                        if line:
                            if line.startswith('cp '):
                                file = line.strip().split()[1].split('/')[-1]
                                files_to_upload_from_scripts.append(file)
                if files_to_upload_from_json:
                    extra_upload_files = list()
                    for file in files_to_upload_from_json:
                        if file not in files_to_upload_from_scripts:
                            extra_upload_files.append(file)
                    if extra_upload_files:
                        logging.warning(f'The files [{" ,".join(extra_upload_files)}] are uploaded but not used!')
                    missing_upload_files = list()
                    for file in files_to_upload_from_scripts:
                        if file not in files_to_upload_from_json:
                            missing_upload_files.append(file)
                    if missing_upload_files:
                        raise NoFileToUploadError(f'The files [{" ,".join(missing_upload_files)}] are needed but not uploaded!')

            main_file.write('}\n')

    def provision(self):
        with open(f'{constants.packer_provs_confs_path}/{self.arguments["-j"]}') as provisions:
            json_provision = json.loads(provisions.read())
        vbox_configs = json_provision['vbox-configs']
        self._generate_vars_file(vbox_configs)
        self._generate_main_file(json_provision)

    def provisioner_shell(self, scripts ,main_file):
        main_file.write(
        '  provisioner "shell" {\n'
        '    binary               = false\n'
        '    execute_command      = "echo ' + "'${" + "var.ssh_password}" + "' | " + '{' + '{' + ' .Vars ' + '}' + '} sudo -S -E bash ' + "'" +  '{' + '{' + ' .Path ' + '}' + '}' + "'" + '"\n'
        '    expect_disconnect    = true\n'
        '    valid_exit_codes     = [0, 2]\n'
        '    scripts = [\n'
        )
        for script in scripts:
            main_file.write(f'      "{script}",\n')
        main_file.write(
            '    ]\n'
            f'  {self._generate_packer_variable("start_retry_timeout")}'
            '  }\n\n'
        )

    def provisioner_file(self, files, main_file):
        main_file.write(
            '  provisioner "file" {\n'
            '    sources = [\n'
        )
        for file in files:
            main_file.write(f'      "{file}",\n')
        main_file.write(
            '    ]\n'
            '    destination = "/vagrant/upload/"\n'
            '  }\n\n'
        )

    def write_variable_directive(self, variable_file, variable_name, description, variable_type, value):
        variable_file.write(
            f'variable "{variable_name}" ' + '{\n'
            f'  description\t= "{description}"\n'
            f'  type\t= {variable_type}\n'
        )
        if variable_type == 'bool' or variable_name == 'boot_command':
            variable_file.write(
                f'  default\t= {value}\n'
            )
        else:
            variable_file.write(
                f'  default\t= "{value}"\n'
            )
        variable_file.write(
            '}\n\n'
        )

    def delete_project(self):
        shutil.rmtree(f'{self.machine_path}/{self.arguments["-n"]}')