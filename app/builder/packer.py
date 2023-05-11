import constants
import json
import os
import shutil
from argparse import Namespace
from builder.builder import Builder
from builder.error import (
    ExistenceProjectError,
    JsonConfigCopiedError,
    ExistenceVirtualBoxError
)
from builder.helper import (
    get_local_virtual_boxes,
    replace_text_in_file,
)


class Packer(Builder):
    def __init__(self, namespace) -> None:
        self.arguments: Namespace = namespace
        self.machines_path: str = constants.packer_machines_path
        self.provisions_configs = constants.packer_provs_confs_path
        self.configs: dict = dict()
        self.provisions: dict = dict()

    def set_configs(self):
        config_provision_file_path = f'{self.provisions_configs}/{self.arguments.json}'
        with open(config_provision_file_path, 'r') as template_json:
            configs = json.loads(template_json.read())["virtual_machine_configs"]
        self.configs = configs.copy()

    def set_provisions(self):
        config_provision_file_path = f'{self.provisions_configs}/{self.arguments.json}'
        with open(config_provision_file_path, 'r') as template_json:
            provisions = json.loads(template_json.read())["provisions"]
        self.provisions = provisions.copy()

    def set_credentials(self):
        config_provision_file_path = f'{self.provisions_configs}/{self.arguments.json}'
        with open(config_provision_file_path, 'r') as template_json:
            credentials = json.loads(template_json.read())["credentials"]
        self.credentials = credentials.copy()

    def check_new_project_folder_existence(self):
        if self.arguments.name in os.listdir(self.machines_path):
            raise ExistenceProjectError("[ERROR] Project already exists!")

    def check_virtualbox_existence(self):
        if self.arguments.vboxname in get_local_virtual_boxes():
            raise ExistenceVirtualBoxError(
                f'The virtualbox {self.arguments.vboxname} already exists!'
            )

    def check_provision_cfg_json_existence(self):
        if self.arguments.json not in os.listdir(self.provisions_configs):
            shutil.copyfile(
                src=f'{self.provisions_configs}/template.json',
                dst=f'{self.provisions_configs}/{self.arguments.json}'
            )
            raise JsonConfigCopiedError(
                f'The json file "{self.arguments.json}" '
                f'is created at {constants.vagrant_provs_confs_path} folder.\n'
                'Fill it up and come back then!'
            )

    def create_project_folder(self):
        project_folder = f'{self.machines_path}/{self.arguments.name}'
        os.makedirs(f'{project_folder}/http')

        shutil.copyfile(
            src=f'{constants.packer_http_path}/{self.arguments.preseed}',
            dst=f'{project_folder}/http/{self.arguments.preseed}'
        )

    def _generate_packer_variable(self, variable: str):
        number = 30
        chars = len(variable)
        space = (number - chars) * ' '
        return f'  {variable}{space}= \"${{var.{variable}}}\"\n'

    def _get_provisions_scripts(self):
        scripts = list()
        for key in self.provisions:
            value = self.provisions[key]
            if value:
                if isinstance(value, bool):
                    script_path = f'{constants.setup_scripts_path}/{key}.sh'
                    scripts.append(script_path)
                elif key == 'custom_scripts':
                    for script in value:
                        scripts.append(
                            f'{constants.custom_scripts_path}/{script}'
                        )
                elif isinstance(value, list):
                    operation = key.split('_')[-1]
                    for program in value:
                        scripts.append(
                            f'{constants.programs_path}/{program}/{operation}.sh'
                        )
        return scripts

    def _generate_vars_file(self, json_file: dict):
        with open(f'{constants.packer_machines_path}/{self.arguments.name}/vars.pkr.hcl', 'w') as vars_file:
            for var in json_file:
                if not isinstance(json_file[var], dict):
                    continue
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
                        lines = boot_command.readlines()
                    for count, line in enumerate(lines):
                        lines[count] = line.replace('preseed-file', self.arguments.preseed)
                    json_file[var]["default"] = ''.join(lines)

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
        with open(f'{constants.packer_machines_path}/{self.arguments.name}/main.pkr.hcl', 'w') as main_file:
            main_file.write(
                'locals {\n'
                f'{self._generate_packer_variable("output_directory")}'
                '}\n\n'
            )
            main_file.write('source "virtualbox-iso" "vbox" {\n')
            # for var in json_file['vbox_configs']:
            for var in self.configs:
                # if not isinstance(json_file['vbox_configs'][var], dict):
                if not isinstance(self.configs[var], dict):
                    continue
                space = (30 - len(var)) * ' '
                if var in ['start_retry_timeout', 'iso_file']:
                    continue
                elif var == 'boot_command':
                    main_file.write(f'  {var}{space}= [ var.{var} ]\n')
                elif var == 'iso_directory':
                    main_file.write(
                        '  iso_target_path               = '
                        '"${var.iso_directory}/${var.iso_file}"\n'
                    )
                elif var == 'iso_link':
                    main_file.write(
                        '  iso_urls = [\n'
                        '    "${var.output_directory}/${var.iso_file}",\n'
                        '    "${var.iso_link}",\n'
                        '  ]\n'
                    )
                elif var == 'ssh_password':
                    main_file.write(
                        '  shutdown_command              = "echo '
                        '\'${var.ssh_password}\' | sudo -E -S poweroff"\n'
                    )
                    main_file.write(self._generate_packer_variable(var))
                else:
                    main_file.write(self._generate_packer_variable(var))
            main_file.write(
                '  vboxmanage = [\n'
                '      ["modifyvm", "{{ .Name }}", "--rtcuseutc", "off"],\n'
                '      ["modifyvm", "{{ .Name }}", "--vram", "128"]\n'
                '  ]\n'
                '  virtualbox_version_file       = "/tmp/.vbox_version"\n'
            )
            main_file.write('}\n\n')

            main_file.write(
                'build {\n\n'
                '  sources = ["source.virtualbox-iso.vbox"]\n\n'
            )

            provision_scripts = self._get_provisions_scripts()

            self.provisioner_shell(
                scripts=provision_scripts,
                main_file=main_file
            )

            upload_program_files_path = list()
            for program in self.provisions['programs']['install']:
                upload_program_files_path.extend([
                    f'{constants.programs_path}/{program}/configs/upload/{file}' 
                    for file in os.listdir(f'{constants.programs_path}/{program}/configs/upload') 
                    if file != 'prepare_to_upload.sh'
                ])
            if self.provisions['upload']:
                files_in_upload_folder = os.listdir(constants.upload_path)
                upload_files = list()
                for file in self.provisions['files_to_upload']:
                    if file in files_in_upload_folder:
                        upload_files.append(
                            f'{constants.upload_path}/{file}'
                        )
                    else:
                        for path in upload_program_files_path:
                            if file in path:
                                upload_files.append(path)

                self.provisioner_file(upload_files, main_file)
            if self.provisions['custom_scripts']:
                custom_scripts = [
                    f'{constants.custom_scripts_path}/{script}'
                    for script in self.provisions['custom_scripts']
                ]
                self.provisioner_shell(
                    scripts=custom_scripts,
                    main_file=main_file
                )
            main_file.write('}\n')

    def _add_user_password_preseed(self, credentials: dict):
        project_folder = f'{self.machines_path}/{self.arguments["-n"]}'
        replace_text_in_file(
            search_phrase="default_user",
            replace_with=credentials['default_user'],
            file_path=f'{project_folder}/http/{self.arguments["-pf"]}'
        )
        replace_text_in_file(
            search_phrase="default_pass",
            replace_with=credentials['default_pass'],
            file_path=f'{project_folder}/http/{self.arguments["-pf"]}'
        )

    def generate_main_file(self):
        with open(f'{constants.packer_provs_confs_path}/{self.arguments.json}') as provisions:
            json_provision = json.loads(provisions.read())
        # vbox_configs = json_provision['vbox_configs']
        self._generate_vars_file(self.configs)
        # self._generate_main_file(json_provision)
        self._generate_main_file(self.configs)
        credentials = {
            key: value for (key, value) in self.configs.items()
            if key in ("default_user", "default_pass")
        }
        self._add_user_password_preseed(credentials)

    def provisioner_shell(self, scripts, main_file):
        main_file.write(
            '  provisioner "shell" {\n'
            '    binary               = false\n'
            '    execute_command      = "echo \'${var.ssh_password}\' | {{ .Vars }} sudo -S -E bash \'{{ .Path }}\'\"\n'
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
        with open(f'{constants.bash_path}/prepare_to_upload.sh', 'r') as preparer:
            lines = preparer.readlines()
        for line in lines:
            if line.startswith('mkdir '):
                upload_folder_path = line.strip().split()[-1]

        main_file.write(
            '    ]\n'
            f'    destination = "{upload_folder_path}"\n'
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
        shutil.rmtree(f'{self.machines_path}/{self.arguments.name}')
