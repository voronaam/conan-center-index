#!/usr/bin/env python3
"""
Copyright (C) 2020 Rene Rivera.
Use, modification and distribution are subject to the
Boost Software License, Version 1.0. (See accompanying file
LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
"""
import os.path
import sys
from pprint import pprint
from bls.util import PushDir
from foreach import ForEach
from cpt.packager import ConanMultiPackager
from conans import tools
from pathlib import Path
from conans.client.conan_api import Conan


script_dir = os.path.dirname(os.path.realpath(__file__))
recipes_dir = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(script_dir))))
root_dir = os.path.dirname(recipes_dir)


class BuildAll(ForEach):
    '''
    Calls CPT for all the Boost packages possible. This runs both
    outside and inside a Docker container. When specifying with the
    ++package option it runs for that one package inside the container.
    Otherwise it runs for all packages outside the container.
    '''

    def __init_parser__(self, parser):
        super(BuildAll, self).__init_parser__(parser)
        parser.add_argument(
            '++base-version',
            help='The version of boost_base package.',
            required=True)
        parser.add_argument(
            '++package',
            help='The single package to build.')

    def groups_pre(self, groups):
        self.build_in_container = False
        self.conan_env = {}
        self.pip_install = []
        if 'CONAN_DOCKER_IMAGE' in os.environ:
            self.conan_env['CONAN_USE_DOCKER'] = '1'
        if tools.os_info.is_linux:
            self.build_in_container = True
            conan_api = conan_api, _, _ = Conan.factory()
            conan_api.create_app()
            self.conan_data_dir = conan_api.config_get("storage.path")
            tools.rmdir(self.conan_data_dir)
            tools.mkdir(self.conan_data_dir)
            self.conan_env["CONAN_DOCKER_RUN_OPTIONS"] \
                = "-v {}:/home/conan/.conan/data".format(self.conan_data_dir)
        if self.build_in_container:
            self.pip_install.append(
                'https://github.com/grafikrobot/boost_lib_stats/archive/master.zip')
        super(BuildAll, self).groups_pre(groups)

    def package_do(self, package):
        super(BuildAll, self).package_do(package)
        package_name = 'boost_'+package
        print('>>>>>>>>>>')
        print('>>>>>>>>>> '+package_name)
        print('>>>>>>>>>>')
        sys.stdout.flush()
        package_version = self.args.version
        if package == 'base':
            package_version = self.args.base_version
        package_dir = os.path.join(
            recipes_dir, package_name, package_version)
        if not os.path.exists(package_dir):
            package_dir = os.path.join(
                recipes_dir, package_name, 'all')
        if os.path.isdir(package_dir):
            with PushDir(package_dir) as _:
                env = self.conan_env.copy()
                env['CONAN_REFERENCE'] = "%s/%s"%(package_name, package_version)
                with tools.environment_append(env):
                    if self.build_in_container:
                        self.__check_call__(['chmod', 'a+w', self.conan_data_dir])
                    builder = ConanMultiPackager(
                        pip_install=self.pip_install,
                        # docker_entry_script='%s %s ++base-version=%s ++package=%s'%(
                        #     os.environ['PYEXE'],
                        #     os.path.realpath(__file__),
                        #     self.args.base_version,
                        #     package)
                        )
                    builder.add_common_builds()
                    builder.run()


if __name__ == "__main__":
    BuildAll()
