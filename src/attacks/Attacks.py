import subprocess


def __make_dir_editable(path):
    bash_command = f'chmod 777 {path}'
    result = subprocess.run(bash_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)


def _do_scan_scapy_attack(log_dir, log_file, destination = '192.168.0.1/24', timeout = 10 ):
    bash_command = ['sudo python3 ',
                    'ics_sim/ScapyAttacker.py',
                    f'--output {log_file}'
                    f'--attack scan',
                    f'--timeout {timeout}',
                    f' --destination {destination}']
    _do_attack(log_dir, log_file, bash_command)


def _do_attack(log_dir, log_file, bash_command):
    __make_dir_editable(log_dir)
    result = subprocess.run(bash_command, shell=True, check=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    __make_dir_editable(log_file)
