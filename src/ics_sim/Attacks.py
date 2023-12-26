import subprocess


def __make_dir_editable(path):
    bash_command = f'chmod 777 {path}'
    subprocess.run(bash_command, shell=True, check=True)


def _do_scan_scapy_attack(log_dir, log_file, destination, timeout=10):
    bash_command = ['python3',
                    'ics_sim/ScapyAttacker.py',
                    '--output', log_file,
                    '--attack', 'scan',
                    '--timeout', str(timeout),
                    '--destination', destination]

    _do_attack(log_dir, log_file, bash_command)


def _do_replay_scapy_attack(log_dir, log_file, destination, timeout=15, replay_count=3, mode='link'):
    bash_command = ['python3',
                    'ics_sim/ScapyAttacker.py',
                    '--output', log_file,
                    '--attack', 'replay',
                    '--mode', mode,
                    '--timeout', str(timeout),
                    '--parameter', str(replay_count),
                    '--destination', destination]

    _do_attack(log_dir, log_file, bash_command)


def _do_mitm_scapy_attack(log_dir, log_file, destination, timeout=30, noise=0.1):
    bash_command = ['python3',
                    'ics_sim/ScapyAttacker.py',
                    '--output', log_file,
                    '--attack', 'mitm',
                    '--timeout', str(timeout),
                    '--parameter', str(noise),
                    '--destination', destination]

    _do_attack(log_dir, log_file, bash_command)


def _do_scan_nmap_attack(log_dir, log_file, destination):
    bash_command = ['nmap -p- -oN $2 192.168.0.1-255',
                    '-p-',
                    '-oN', log_file,
                    destination]

    _do_attack(log_dir, log_file, bash_command)


def _do_command_injection_attack(log_dir, log_file, command_injection_agent, command_counter=30):
    bash_command = ['python3',
                    command_injection_agent,
                    str(command_counter)]

    _do_attack(log_dir, log_file, bash_command)


def _do_ddos_attack(log_dir, log_file, ddos_agent_path, num_process, destination):
    processes = []
    for i in range(num_process):
        processes.append(f'python3 {ddos_agent_path} A{i} {destination} {log_file}')

    bash_command = '& '.join(processes)
    _do_attack(log_dir, log_file, bash_command)


def _do_attack(log_dir, log_file, bash_command):
    __make_dir_editable(log_dir)
    print(bash_command)
    subprocess.run(bash_command)
    __make_dir_editable(log_file)
