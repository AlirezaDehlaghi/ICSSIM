import subprocess


def __make_dir_editable(path):
    bash_command = f'chmod 777 {path}'
    subprocess.run(bash_command, shell=True, check=True)


def _do_scan_scapy_attack(log_dir, log_file, target, timeout=10):
    bash_command = ['python3',
                    'ics_sim/ScapyAttacker.py',
                    '--output', log_file,
                    '--attack', 'scan',
                    '--timeout', str(timeout),
                    '--target', target]

    _do_attack(log_dir, log_file, bash_command)


def _do_replay_scapy_attack(log_dir, log_file, target, timeout=15, replay_count=3):
    bash_command = ['python3',
                    'ics_sim/ScapyAttacker.py',
                    '--output', log_file,
                    '--attack', 'replay',
                    '--timeout', str(timeout),
                    '--parameter', str(replay_count),
                    '--target', target]

    _do_attack(log_dir, log_file, bash_command)


def _do_mitm_scapy_attack(log_dir, log_file, target, timeout=30, noise=0.1):
    subprocess.run(['echo', '0'], stdout=open('/proc/sys/net/ipv4/ip_forward',"w"))
    bash_command = ['python3',
                    'ics_sim/ScapyAttacker.py',
                    '--output', log_file,
                    '--attack', 'mitm',
                    '--timeout', str(timeout),
                    '--parameter', str(noise),
                    '--target', target]

    _do_attack(log_dir, log_file, bash_command)
    subprocess.run(['echo', '1'], stdout=open('/proc/sys/net/ipv4/ip_forward',"w"))


def _do_scan_nmap_attack(log_dir, log_file, target):
    bash_command = ['nmap',
                    '-p-',
                    '-oN', log_file,
                    target]

    _do_attack(log_dir, log_file, bash_command)


def _do_command_injection_attack(log_dir, log_file, command_injection_agent, command_counter=30):
    bash_command = ['python3',
                    command_injection_agent,
                    str(command_counter)]

    _do_attack(log_dir, log_file, bash_command)


def _do_ddos_attack(log_dir, log_file, ddos_agent_path, timeout,  num_process, target):
    __make_dir_editable(log_dir)
    processes_args = []
    processes = []
    for i in range(num_process):
        processes_args.append(f'python3 {ddos_agent_path} Agent{i} --timeout {timeout} --target {target} --log_path {log_file}'.split(' '))

    for i in range(num_process):
        processes.append(subprocess.Popen(processes_args[i]))
     
    for i in range(num_process):
        processes[i].wait()
        
    print('execution finished')  
    __make_dir_editable(log_file)


def _do_attack(log_dir, log_file, bash_command):
    __make_dir_editable(log_dir)
    print(bash_command)
    subprocess.run(bash_command)
    __make_dir_editable(log_file)
