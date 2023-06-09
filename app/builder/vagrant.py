import constants
import os
import shutil
from builder.builder import Builder
from builder.error import (
    NoFileToUploadError,
)
from builder.helper import (
    get_packages_upload_files,
    is_empty_script,
    replace_text_in_file,
)
from typing import List


class Vagrant(Builder):
    def __init__(self, json_file: dict) -> None:
        self.provisions_configs = json_file
        self.machine_path: str = constants.VAGRANT_MACHINES_PATH
        self.vagrantfile_path = (
            f'{self.machine_path}/'
            f'{self.provisions_configs["configurations"]["project_name"]["default"]}/'
            'Vagrantfile'
        )
        self.configs: dict = dict()
        self.provisions: dict = dict()
        self.credentials: dict = dict()

    def set_configs(self):
        """Set configs attribute"""
        self.configs = self.provisions_configs["configurations"].copy()

    def set_provisions(self):
        """Set provisions attribute"""
        self.provisions = self.provisions_configs["provisions"].copy()

    def set_credentials(self):
        """Set credentials attribute"""
        self.credentials = self.provisions_configs["credentials"].copy()

    def create_project_folder(self):
        """
        Create project folder with this structure:
        - project_name/
            |
            - upload/
        """
        project_folder = f'{self.machine_path}/{self.configs["project_name"]["default"]}'
        # create project folder
        if os.path.exists(project_folder):
            shutil.rmtree(project_folder)
        os.mkdir(project_folder)

        # create upload folder
        os.mkdir(f'{project_folder}/upload')

    def _generate_provision_section(self, src, title: str, package: str):
        """
        Generate provision section in Vagrantfile.
        It titles section as follow
            ######################################################################
            echo ==OPERATION package==============================================
            ######################################################################
        """
        hash_number = 70
        with open(src, 'r') as source_file:
            lines = source_file.readlines()

        if "create_extra_user.sh" in src:
            lines = [line.replace("extra_user", self.credentials["extra_user"]) for line in lines]

        if title.lower() in ['config'] and is_empty_script(src):
            pass
        else:
            with open(
                f'{self.machine_path}/{self.configs["project_name"]["default"]}/Vagrantfile',
                'a'
            ) as vagrantfile:
                vagrantfile.write(f'\n\n\t\t{hash_number*"#"}\n')
                pound_number = hash_number - 8 - len(title) - len(package)
                # vagrantfile.write(f'\t#######   {title} {package}   {pound_number*"#"}')
                vagrantfile.write(f'\t\techo =={title} {package}{pound_number*"="}')
                vagrantfile.write(f'\n\t\t{hash_number*"#"}\n')

                for line in lines:
                    if line in ['#!/bin/bash', '#!/bin/bash\n']:
                        continue
                    vagrantfile.write(f'\t\t{line.strip()}\n')

    def _copy_configurations_to_upload(self, packages: List[str]):
        """
        Find needed files from config.sh script and copy them into project
        upload folder
        """
        packages_files_upload = get_packages_upload_files(
            packages=packages
        )
        missing_upload_files = str()
        for package in packages_files_upload:
            for upload_file in packages_files_upload[package]:
                try:
                    shutil.copyfile(
                        src=f'{constants.PACKAGES_PATH}/{package}/upload/{upload_file}',
                        dst=f'{self.machine_path}/{self.configs["project_name"]["default"]}/upload/{upload_file}'
                    )
                except FileNotFoundError:
                    missing_upload_files += f'"{upload_file}" from "{package}"\n'
                if upload_file == "motd":
                    replace_text_in_file(
                        search_phrase="extra_user",
                        replace_with=self.credentials["extra_user"],
                        file_path=f'{self.machine_path}/{self.configs["project_name"]["default"]}/upload/{upload_file}'
                    )
        if missing_upload_files:
            raise NoFileToUploadError(
                'You specify files to upload that does not exist.\n'
                'These are:\n'
                f'{missing_upload_files}'
            )

    def _initialize_vagrantfile(self):
        """Add initial configurations to Vagrantfile"""
        connection = 'true' if self.configs["connection"]["default"] == 'key' else 'false'
        with open(self.vagrantfile_path, 'w') as vagrantfile:
            vagrantfile.write(
                '# -*- mode: ruby -*-\n'
                '# vi: set ft=ruby :\n\n'
            )
            vagrantfile.write(
                'Vagrant.configure("2") do |config|\n'
                f'\tconfig.vm.box = "{self.configs["image"]["default"]}"\n'
                f'\tconfig.ssh.username = "{self.credentials["username"]}"\n'
                f'\tconfig.ssh.password = "{self.credentials["password"]}"\n'
                f'\tconfig.ssh.insert_key = {connection}\n'
                f'\tconfig.vm.hostname = \"{self.configs["hostname"]["default"]}\"\n'
                f'\tconfig.vm.define "{self.configs["hostname"]["default"]}"\n'
                f'\tconfig.vm.provider :{self.configs["provider"]["default"]} do |vb|\n'
                f'\t\tvb.name = "{self.configs["vbox_name"]["default"]}"\n'
                '\t\tvb.gui = true\n'
                '\t\tvb.customize ["modifyvm", :id, "--uart1", "0x3f8", "4"]\n'
                f'\t\tvb.memory = {self.configs["memory"]["default"]}\n'
                f'\t\tvb.cpus = {self.configs["cpus"]["default"]}\n'
            )
            for nic in self.configs["networks"]:
                # we do not touch nic1 since it is reserved for vagrant
                if nic == 'nic1':
                    continue
                # check if nic is enabled
                if self.configs["networks"][nic]["enable"]:
                    # check if nic is hostonly type
                    if self.configs["networks"][nic]["nic_type"] == 'hostonly':
                        vagrantfile.write(
                            f'\t\tvb.customize ["modifyvm", :id, "--{nic}", "{self.configs["networks"][nic]["nic_type"]}"]\n'
                            f'\t\tvb.customize ["modifyvm", :id, "--hostonlyadapter{nic[-1]}", "{self.configs["networks"][nic]["settings"]["hostonly"]}"]\n'
                            f'\t\tvb.customize ["modifyvm", :id, "--cableconnected{nic[-1]}", "on"]\n'
                        )
                    # check if nic is bridged type
                    if self.configs["networks"][nic]["nic_type"] == 'bridged':
                        vagrantfile.write(
                            f'\t\tvb.customize ["modifyvm", :id, "--{nic}", "{self.configs["networks"][nic]["nic_type"]}"]\n'
                            f'\t\tvb.customize ["modifyvm", :id, "--bridgeadapter{nic[-1]}", "{self.configs["networks"][nic]["settings"]["bridge"]}"]\n'
                            f'\t\tvb.customize ["modifyvm", :id, "--cableconnected{nic[-1]}", "on"]\n'
                        )
                    # check if nic is natnetwork type
                    if self.configs["networks"][nic]["nic_type"] == 'natnetwork':
                        vagrantfile.write(
                            f'\t\tvb.customize ["modifyvm", :id, "--{nic}", "{self.configs["networks"][nic]["nic_type"]}"]\n'
                            f'\t\tvb.customize ["modifyvm", :id, "--natnetwork{nic[-1]}", "{self.configs["networks"][nic]["settings"]["natnetwork"]}"]\n'
                            f'\t\tvb.customize ["modifyvm", :id, "--cableconnected{nic[-1]}", "on"]\n'
                        )
            vagrantfile.write(
                '\tend\n'
                f'\tconfig.vm.disk :disk, size: "{self.configs["disk_size"]["default"]}MB", name: "default", primary: true'
            )

    # def _write_network_settings()

    def generate_main_file(self):
        """
        Generate Vagrantfile following the instructions from JSON file
        """
        self._initialize_vagrantfile()
        with open(self.vagrantfile_path, 'a') as vagrantfile:
            vagrantfile.write('\n\tconfig.vm.provision "shell", inline: <<-SHELL\n')
        if self.credentials["extra_user"]:
            self._generate_provision_section(
                    src=f'{constants.SETUP_SCRIPTS_PATH}/create_extra_user.sh',
                    title=f'CREATE USER {self.credentials["extra_user"]}',
                    package=''
                )
        if self.provisions['update_upgrade']:
            self._generate_provision_section(
                    src=f'{constants.SETUP_SCRIPTS_PATH}/update_upgrade.sh',
                    title="UPDATE and UPGRADE",
                    package='apt'
                )
        if self.provisions['update_upgrade_full']:
            self._generate_provision_section(
                    src=f'{constants.SETUP_SCRIPTS_PATH}/update_upgrade_full.sh',
                    title="UPDATE and UPGRADE FULL",
                    package='apt'
                )
        if self.provisions['packages_to_install']:
            for package in self.provisions['packages_to_install']:
                self._generate_provision_section(
                    src=f'{constants.PACKAGES_PATH}/{package}/install.sh',
                    title="INSTALL",
                    package=package
                )
        if self.provisions['packages_to_config']:
            for package in self.provisions['packages_to_config']:
                self._generate_provision_section(
                    src=f'{constants.PACKAGES_PATH}/{package}/config.sh',
                    title="CONFIG",
                    package=package
                )
            self._copy_configurations_to_upload(
                packages=self.provisions['packages_to_config']
            )
        if self.provisions['packages_to_uninstall']:
            for package in self.provisions['packages_to_uninstall']:
                self._generate_provision_section(
                    src=f'{constants.PACKAGES_PATH}/{package}/uninstall.sh',
                    title="UNINSTALL",
                    package=package
                )
        if self.provisions['clean_packages']:
            self._generate_provision_section(
                src=f'{constants.SETUP_SCRIPTS_PATH}/clean_packages.sh',
                title="CLEAN apt packages",
                package=''
            )
        if self.provisions['reboot']:
            self._generate_provision_section(
                src=f'{constants.SETUP_SCRIPTS_PATH}/reboot.sh',
                title="REBOOT",
                package=''
            )
        if self.provisions['custom_scripts']:
            for script in self.provisions['custom_scripts']:
                self._generate_provision_section(
                    src=f'{constants.CUSTOM_SCRIPTS_PATH}/{script}',
                    title="CUSTOM SCRIPT",
                    package=f'{script.split(".")[0]}'
                )

        with open(self.vagrantfile_path, 'a') as vagrantfile:
            vagrantfile.write('\n\nSHELL\nend')

        if self.credentials["extra_user"]:
            replace_text_in_file(
                search_phrase='extra_user',
                replace_with=self.credentials["extra_user"],
                file_path=f'{self.machine_path}/{self.configs["project_name"]["default"]}/Vagrantfile'
            )

    def delete_project(self):
        shutil.rmtree(f'{self.machine_path}/{self.configs["project_name"]["default"]}')
