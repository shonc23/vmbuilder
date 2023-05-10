import subprocess
import os
import constants


def get_json_files_for_help(path_to_provs_confs: str):
    """
    Return json files available but template.json as string.\n
    Each name is separated by a pipe.
    """
    provision_files = [
            file for file in os.listdir(
                path_to_provs_confs
            ) if file != 'template.json'
        ]
    if not provision_files:
        message = (
            'There are no JSON files. '
            'To create a new one is sufficient to specify it '
            'using the relative JSON flag from the main app. '
        )
    else:
        message = 'Select among: '
        message += ' | '.join(
            [
                f'{file}' for file in provision_files
            ]
        )
    return message


def get_preseed_files_for_help():
    """
    Return preseed file names available in http folder for packer machines
    as string.\n
    Each name is separated by a pipe.
    """
    help_message = 'Select among: '
    help_message += " | ".join(
        [
            f'{file}' for file in os.listdir(
                constants.packer_http_path
            ) if file.startswith('preseed')
        ]
    )
    return help_message


def get_local_vagrant_boxes():
    """
    Return installed vagrant box list as string.\n
    Each vagrant box name is separated by a pipe.
    """
    output = subprocess.run(
        "vagrant box list",
        shell=True,
        capture_output=True
    ).stdout.decode("ascii").strip().replace("\n", " | ")
    return output


def replace_text_in_file(search_phrase, replace_with, file_path):
    replaced_content = ""
    with open(file_path, "r") as file:
        for line in file:
            line = line.rstrip()
            new_line = line.replace(search_phrase, replace_with)
            replaced_content = replaced_content + new_line + '\n'
    with open(file_path, "w") as new_file:
        new_file.write(replaced_content)


def get_local_virtual_boxes():
    """
    Return the virtual machine names list as string.
    """
    vmbox_list = subprocess.run(
        "VBoxManage list vms",
        shell=True,
        capture_output=True
    ).stdout.decode("ascii")
    return vmbox_list


def is_empty_script(script: str):
    """
    Return True the given script is empty
    """
    with open(script) as script_file:
        lines = script_file.readlines()

    for line in lines:
        if line in ['#!/bin/bash', '#!/bin/bash\n']:
            lines.remove(line)

    return not any(lines)


def get_programs_upload_files(programs: list) -> dict:
    """
    Return a dictionary with programs as keys and list of
    upload file names as value
    """
    program_upload_files = dict()
    for program in programs:
        with open(
            f'{constants.programs_path}/{program}/config.sh', 'r'
        ) as file:
            lines = file.readlines()
        program_upload_files[program] = list()
        for line in lines:
            if line.startswith('cp '):
                upload_file_name = line.strip().split()[1].split('/')[-1]
                program_upload_files[program].append(
                    upload_file_name
                )
    return program_upload_files
