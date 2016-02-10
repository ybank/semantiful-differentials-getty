# system calls

import subprocess


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
