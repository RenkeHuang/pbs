import sys
import os
import re
import subprocess

def generate_pbs_script(filename, path, queue_name, n_nodes, ppn, template_file):
    """This function creates and saves a PBS batch script to submit a Single Processor job
       in the current working directory.

    Parameters
    ----------
    filename(str): name of the executable to run in the PBS job
    path(str): absolute path to the executable
    queue_name(str): default 'high'
    n_nodes(int): number of nodes to run the job, default 1 (single processor job)
    ppn(int): number of processors per node, default 1 (single processor job)
    template_file(str): name of a PBS script template file

    Returns
    -------
    pbs_file(str): name of the saved PBS script file
    """
    if template_file is None:
        template_file = '/home/renke/_pbs_temp'
    pbs_template = []
    with open(template_file, 'r') as stream:
        for line in stream:
            pbs_template += [line]

    # Populate contents of pbs script file based on parameters.
    pbs_content = [re.sub('&job_name',filename.rstrip('.py'), line) for line in pbs_template]

    pbs_content = [re.sub('&job_errfile_name', filename.rstrip('.py')+".err", line) for line in pbs_content]

    pbs_content = [re.sub('&job_outfile_name', filename.rstrip('.py')+".out", line) for line in pbs_content]

    pbs_content = [re.sub('&path_to_executable_program_name', os.path.join(path, filename), line) 
                    for line in pbs_content]

    pbs_content = [re.sub('&queue_name', queue_name, line) for line in pbs_content]

    pbs_content = [re.sub('&n_nodes', str(n_nodes), line) for line in pbs_content]

    pbs_content = [re.sub('&ppn', str(ppn), line) for line in pbs_content]


    # write PBS file and return name
    pbs_file = os.path.join(path, f"PBS_{filename.rstrip('.py')}.sh")
    with open(pbs_file, 'w') as stream:
        stream.write(''.join(pbs_content))
    
    return pbs_file


def run_pybatch(filename, path, queue_name='high',n_nodes=1, ppn=1, template_file=None):
    print('Generating PBS script......')
    print(f'Try to use {n_nodes} node(s), ppn={ppn}......')
    pbs_file = generate_pbs_script(filename, path, queue_name, n_nodes, ppn, template_file)
    print('PBS script generated.')
    try:
        process = subprocess.Popen(['chmod','764',pbs_file])
        process = subprocess.Popen(['qsub', pbs_file])
        print(f'Submitted to quene {queue_name}')
        process.wait()
    except:
        print(f'job {filename} failed.')
        process.kill()

if __name__ == "__main__":
    """
    $ cd &DIR_OF_JOB_PYTHONFILE
    $ python ~/run_pybatch.py &NAME_OF_PYTHONFILE
    """
    filename = sys.argv[1]
    path = os.getcwd()

    run_pybatch(filename, path, queue_name='low', n_nodes=1, ppn=2)



  

