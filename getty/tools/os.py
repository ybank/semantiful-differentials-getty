# system calls

import subprocess
import sys


def sys_call(cmd, ignore_bad_exit=False):
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        print "\n-- << non-zero exit status code >> --"
        if ignore_bad_exit:
            print "Exit from command: \n\t" + cmd
            print "But we can safely ignore such non-zero exit status code this time.\n"
        else:
            print "Error in command: \n\t" + cmd + "\n"
            raise SystemExit("system exit: " + str(ret))


def from_sys_call(cmd):
    return subprocess.check_output(cmd, shell=True)


# get result from sys_call even if the exit code is not zero
def from_sys_call_enforce(cmd):
    try:
        return subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as ex:
        if ex.returncode != 1:
            raise
        else:
            return ex.output


# copy
def copy_file(from_path, to_path):
    sys_call(" ".join(["cp", from_path, to_path]))


# remove
def remove_file(file_path):
    sys_call(" ".join(["rm", file_path]), ignore_bad_exit=True)


# remove a lot of files - use with care!
def remove_many_files(dir, ptn):
    from_sys_call_enforce("find " + dir +" -name \"" + ptn + "\" -print0 | xargs -0 rm")


# helper to replace last occurrence of a string to something else
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


# change file name to replace last '-hash-' to real hash
def update_file_hash(f, hs):
    nf = rreplace(f, '-hash-', hs, 1)
    sys_call(" ".join(["mv", f, nf]), ignore_bad_exit=True)
    

# merge all dyn info files, create a new one and remote all others
def merge_dyn_files(dyng_go, go, file_part_name, hs):
    related = from_sys_call(" ".join(["ls", dyng_go, "|", "grep", file_part_name]))
    all_files = [dyng_go + t.strip() for t in related.strip().split("\n")]
    concat_list_str = "["
    for onefile in all_files:
        with open(onefile, 'r') as rf:
            content = rf.read().strip()
            if content.startswith("[") and content.endswith("]"):
                concat_list_str += content[1:-1]
        remove_file(onefile)
    concat_list_str += "]"
    new_file = go + rreplace(file_part_name, '-hash-', hs, 1)
    with open(new_file, 'w') as wf:
        wf.write(concat_list_str)


# get pwd
def cwd():
    return from_sys_call("pwd").strip()


# define project name to be the (default) folder name
def project_name(pwd):
    pwd = pwd.strip()
    if pwd.endswith("/"):
        pwd = pwd[:-1]
    lsi = pwd.rfind("/")
    return pwd[lsi+1:]


# Print iterations progress
def print_progress (iteration, total, prefix='', suffix='', decimals=2, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int) 
        bar_length   - Optional  : character length of bar (Int) 
    """
    filledLength    = int(round(bar_length * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (bar_length - filledLength)
    sys.stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        print("\n")
