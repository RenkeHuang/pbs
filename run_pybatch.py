#!/opt/intel/intelpython3/bin/python

import sys
import os
import re
import subprocess
import argparse


def generate_pbs_script(filename, path, queue_name, n_nodes, ppn,
                        template_file):
    """This function creates a PBS batch script to submit a Single Processor job
       in the current working directory.

    Parameters
    ----------
    filename(str): name of the executable to run in the PBS job
    path(str): absolute path to the executable
    queue_name(str): default 'high'
    n_nodes(int): number of nodes to run the job, default 1 (single processor job)
    ppn(int): number of processors per node, default 1 (single processor job)
    template_file(str): (optional) name of a PBS script template file

    Returns
    -------
    pbs_file(str): name of the saved PBS script file
    """
    if template_file is None:
        temp_file = '/home/renke/_pbs_temp'
    else:
        temp_file = os.path.join(os.getcwd(), template_file)

    pbs_template = []

    with open(temp_file, 'r') as stream:
        for line in stream:
            pbs_template += [line]

    # Populate contents of pbs script file based on parameters.
    pbs_content = [
        re.sub('&job_name', filename.rstrip('.py'), line)
        for line in pbs_template
    ]

    pbs_content = [
        re.sub('&job_errfile_name',
               filename.rstrip('.py') + ".err", line) for line in pbs_content
    ]

    pbs_content = [
        re.sub('&job_outfile_name',
               filename.rstrip('.py') + ".out", line) for line in pbs_content
    ]

    pbs_content = [
        re.sub('&path_to_executable_program_name',
               os.path.join(path, filename), line) for line in pbs_content
    ]

    pbs_content = [
        re.sub('&queue_name', queue_name, line) for line in pbs_content
    ]

    pbs_content = [
        re.sub('&n_nodes', str(n_nodes), line) for line in pbs_content
    ]

    pbs_content = [re.sub('&ppn', str(ppn), line) for line in pbs_content]

    # write PBS file and return name
    pbs_file = os.path.join(path, f'{filename.rstrip(".py")}.pbs')
    with open(pbs_file, 'w') as stream:
        stream.write(''.join(pbs_content))

    return pbs_file


def run_pybatch(filename,
                path,
                queue_name='high',
                n_nodes=1,
                ppn=1,
                template_file=None,
                no_submit=False):
    print(f'Generating PBS script for {os.path.join(path, filename)}')
    print(f'User requests quene "{queue_name}", {n_nodes} node(s), ppn = {ppn}')
    pbs_file = generate_pbs_script(filename, path, queue_name, n_nodes, ppn,
                                   template_file)
    print('PBS script generated.\n')
    try:
        process = subprocess.Popen(['chmod', '764', pbs_file])
        if not no_submit:
            process = subprocess.Popen(['qsub', pbs_file])
            print(f'Submitted to quene {queue_name}')
            process.wait()
    except:
        print(f'job {filename} failed.')
        process.kill()


def _main():
    """
    basic usage:
    $ cd &DIR_OF_JOB_PYTHONFILE
    $ ~/run_pybatch &NAME.py
    For help, 
    $ ~/run_pybatch -h
    """

    cli_parser = argparse.ArgumentParser(
        description="Create a PBS batch script for Python, and qsub the job.",
        add_help=True)
    cli_parser.version = '0.1'
    cli_parser.add_argument(
        'filename',
        metavar='NAME.py',
        help='the name of the python file you want to submitt as a PBS job')
    cli_parser.add_argument(
        'path',
        action='store',
        nargs='?',
        default=os.getcwd(),
        help='the path of the python file you want to submitt as a PBS job')
    cli_parser.add_argument(
        '-q',
        '--queue_name',
        action='store',
        default='low',
        help='set the name of the queue to run the PBS job')
    cli_parser.add_argument('-n',
                            '--n_nodes',
                            type=int,
                            default=1,
                            help='set the number of node(s)')
    cli_parser.add_argument('--ppn',
                            action='store',
                            type=int,
                            default=1,
                            help='set the number of processor(s) per node')
    cli_parser.add_argument(
        '-t',
        '--template',
        action='store',
        type=str,
        metavar='TEMPLATE_FILE_NAME',
        help=
        'use a specific PBS template which resides in the current working directory. If None, the template used is "/home/renke/_pbs_temp"'
    )
    cli_parser.add_argument(
        '--no_sub',
        action='store_true',
        help='use this flag to only create the PBS and not qsub it')

    args = cli_parser.parse_args()

    run_pybatch(args.filename,
                args.path,
                queue_name=args.queue_name,
                n_nodes=args.n_nodes,
                ppn=args.ppn,
                template_file=args.template,
                no_submit=args.no_sub)


if __name__ == "__main__":
    _main()
