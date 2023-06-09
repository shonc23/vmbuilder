import argparse
import logging
import sys
import constants
from argparse import RawTextHelpFormatter
from argumentparser.helper import (
    get_json_files_for_help,
    get_local_vagrant_boxes,
    get_preseed_files_for_help
)

logger = logging.getLogger('vmbuilder')


class CustomArgumentParser:

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog='vmbuilder',
            description='Create a virtual machines, Vagrant or Packer',
            formatter_class=RawTextHelpFormatter
        )
        if not sys.argv[1:]:
            logger.error('Need arguments. Specify "-h/--help" for more info')
            exit()
        elif sys.argv[1:][0] in ['-h', '--help']:
            self.parse_all_arguments()

    def get_namespace(self):
        """Return the namespace after vagrant or packer is specified"""
        self.add_common_args()
        common_namespace, _ = self.parser.parse_known_args()
        if common_namespace.vm_type == 'vagrant':
            self.add_vagrant_args()
        elif common_namespace.vm_type == 'packer':
            self.add_packer_args()

        return self.parser.parse_args()

    def add_common_args(self):
        """Add flags common with both Vagrant and Packer"""
        self.parser.add_argument(
            '-n', required=True, dest='name'
        )
        self.parser.add_argument(
            '-vm', required=True, dest='vm_name'
        )
        self.parser.add_argument(
            '-t',
            dest='vm_type',
            choices=['vagrant', 'packer'],
            required=True
        )
        self.parser.add_argument(
            '-d',
            dest='debug',
            action='store_true',
            required=False
        )

    def parse_all_arguments(self):
        self.add_common_args()
        self.add_vagrant_args()
        self.add_packer_args()
        self.parser.parse_args()

    def add_vagrant_args(self):
        """Parse vagrant argument"""
        vagrant_flags = self.parser.add_argument_group(
            'Vagrant flags',
            'manage vagrant flags'
        )
        vagrant_flags.add_argument('-u', dest='user', required=False)
        vagrant_flags.add_argument('-o', dest='hostname',
                                   required=True)
        vagrant_flags.add_argument(
            '-i',
            dest='image',
            help=get_local_vagrant_boxes(),
            required=True
        )
        vagrant_flags.add_argument(
            '-vj',
            dest='json',
            help=get_json_files_for_help(
                constants.VAGRANT_PROVS_CONFS_PATH
            ),
            required=True
        )
        vagrant_flags.add_argument(
            '-s',
            dest='connection',
            choices=['password', 'key'],
            required=True
        )

    def add_packer_args(self):
        """Parse packer argument"""
        packer_flags = self.parser.add_argument_group(
            'Packer flags',
            'manage packer flags'
        )
        packer_flags.add_argument('-il', dest='iso_link', required=True)
        packer_flags.add_argument('-if', dest='iso_file', required=True)
        packer_flags.add_argument('-cs', dest='iso_checksum', required=True)
        packer_flags.add_argument(
            '-pj',
            dest='json',
            help=get_json_files_for_help(
                constants.PACKER_PROVS_CONFS_PATH
            ),
            required=True
        )
        packer_flags.add_argument(
            '-pf',
            dest='preseed',
            help=get_preseed_files_for_help(),
            required=True
        )
