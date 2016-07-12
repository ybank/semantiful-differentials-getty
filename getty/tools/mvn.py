# maven calls

import subprocess

from tools.os import sys_call


# FIXME: support multi-module project
def path_from_mvn_call(env):
    if env not in ["sourceDirectory", "scriptSourceDirectory", "testSourceDirectory", 
                   "outputDirectory", "testOutputDirectory", "directory"]:
        raise ValueError("incorrect env var: " + env)
    mvn_cmd = "mvn help:evaluate -Dexpression=project.build." + env + " | grep ^/"
    return subprocess.check_output(mvn_cmd, shell=True).strip()


# IMPROVE: supported multi-module project, but make it module-specific when needed
def classpath_from_mvn_call():
    mvn_cmd = "mvn dependency:build-classpath | grep ^\/"
    output = subprocess.check_output(mvn_cmd, shell=True).strip()
    all_paths = set()
    classpaths = output.split("\n")
    for classpath in classpaths:
        classpath = classpath.strip()
        for one_path in classpath.split(":"):
            if one_path not in all_paths:
                all_paths.add(one_path)
    merged = "."
    for path in all_paths:
        merged += (":" + path)
    return merged


# without considering target folders
def full_env_classpath():
    return classpath_from_mvn_call() + ":$CLASSPATH"


# include target folders
def full_classpath(junit_path, sys_classpath, bin_output, test_output):
    return ":".join([junit_path, classpath_from_mvn_call(), sys_classpath, bin_output, test_output])


# get junit version, runner, and test classes
# do not handle the case when a project uses more than one testing tools (junit3 and junit4, or even testng)
# IMPROVE: handle the above case, by creating multiple trace files and merge for invariants
def junit_torun_str():
    mvn_cmd = "mvn org.apache.maven.plugins:maven-surefire-plugin:2.19.2-SNAPSHOT:test | grep ^__for__getty__\ __junit"
    output = subprocess.check_output(mvn_cmd, shell=True).strip().split("\n")
    merged_run = {}
    for junit_torun in output:
        junit_torun = junit_torun.strip()
#         vsn = junit_torun[17:23]
        to_run_list = junit_torun[26:].split(" ")
        runner = to_run_list[0]
        test_classes = set(to_run_list[1:])
        if runner in merged_run:
            merged_run[runner] = (test_classes | merged_run[runner])
        else:
            merged_run[runner] = test_classes
    if len(merged_run) < 1:
        raise NotImplementedError("this project is not using junit")
    elif len(merged_run) == 1:
        junit_runner = merged_run.keys()[0]
        return " ".join([junit_runner] + list(merged_run[junit_runner]))
    else:
        raise NotImplementedError("multiple unhandled test tools are used in this project")


# include coverage report for compare
def generate_coverage_report(go, curr_hash):
    sys_call("mvn emma:emma", ignore_bad_exit=True)
    mvn_cmd = "mvn help:evaluate -Dexpression=project.build.directory | grep ^/"
    emma_dir = subprocess.check_output(mvn_cmd, shell=True).strip() + "/site/emma"
    target_dir = go + "_getty_emma_" + curr_hash + "_"
    sys_call(" ".join(["mv", emma_dir, target_dir]), ignore_bad_exit=True)
