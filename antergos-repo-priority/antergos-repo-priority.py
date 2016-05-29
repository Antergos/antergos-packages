#!/bin/python

import re
import os
from termcolor import colored, cprint


class AntergosRepoPriority:

    pmconf = '/etc/pacman.conf'
    pmconf_new = '/etc/pacman.conf.pacnew'

    def __init__(self):
        self.read_from = self.pmconf_new if os.path.exists(self.pmconf_new) else self.pmconf
    
    def get_pacman_config_contents(self):
        contents = []
        
        with open(self.read_from, 'r') as pacman_config:
            contents.extend(pacman_config.readlines())
        
        return contents
    
    def antergos_repo_before_arch_repos(self):
        seen_antergos = False
        
        for line in self.get_pacman_config_contents():
            if re.search(r'^\[antergos\]', line):
                seen_antergos = True
            if re.search(r'^\[core\]', line):
                break

        return seen_antergos
     
    def get_antergos_repo_lines(self):
        lines = []
        entered_antergos = False

        for line in self.get_pacman_config_contents():
            if entered_antergos and re.match(r'^(\[\w)|(#\[\w)', line):
                break
            elif entered_antergos:
                lines.append(line)
                continue
            elif re.match(r'^\[antergos\]', line):
                lines.append(line)
                entered_antergos = True
         
        return lines
     
    def change_antergos_repo_priority(self):
        antergos_repo_lines = self.get_antergos_repo_lines()
        new_contents = []

        for line in self.get_pacman_config_contents():
            if re.match(r'^\[core\]', line):
                new_contents.extend(antergos_repo_lines)
                new_contents.append('')

            if line not in antergos_repo_lines:
                new_contents.append(line)
             
        with open(self.pmconf_new, 'w') as new_pacman_config:
            new_pacman_config.write(''.join(new_contents))

    def print_notice_to_stdout(self):
        prefix = colored('*', color='red', attrs=['bold', 'blink'])

        cprint(
            '            =======>>> ATTENTION! <<<=======            ',
            color='white',
            on_color='on_red',
            attrs=['bold', 'blink']
        )
        print('')
        print('{} The antergos repo priority has been updated.'.format(prefix))
        print('{} You should review the change in /etc/pacman.conf.pacnew'.format(prefix))
        print('{} and then update your pacman.conf accordingly.'.format(prefix))
        print('')
        cprint(
            '                                                        ',
            color='white',
            on_color='on_red',
            attrs=['bold', 'blink']
        )


if __name__ == '__main__':
    repo_priority = AntergosRepoPriority()

    if not repo_priority.antergos_repo_before_arch_repos():
        print('Changing antergos repo priority in pacman.conf.pacnew...')
        repo_priority.change_antergos_repo_priority()
        repo_priority.print_notice_to_stdout()
