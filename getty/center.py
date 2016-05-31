# all Daikon's usage for invariant analysis

import re

import agency
from tools import daikon, git, mvn, os


# relative path of getty output path (go), when pwd is root dir of project
def rel_go(go):
    if go.endswith("/"):
        go = go[:-1]
    lsi = go.rfind("/")
    return ".." + go[lsi:] + "/"


# sort invariants in the output invariant text file
def sort_txt_inv(out_file):
    inv_map = {}
    current_key = None
    with open(out_file, 'r') as f:
        lines = f.read().strip().split("\n")
        if lines != ['']:
            for line in lines:
                line = line.strip()
                if line.startswith("================"):
                    current_key = None
                elif re.match(".*:::(ENTER|EXIT|CLASS|OBJECT|THROW).*", line):
                    current_key = line
                    inv_map[current_key] = []
                else:
                    inv_map[current_key].append(line)
    with open(out_file, 'w') as f:
        if lines != [''] and len(inv_map):
            for title in sorted(inv_map):
                f.write("\n================\n")
                f.write(title + "\n")
                for inv in sorted(inv_map[title]):
                    f.write(inv + "\n")
        else:
            f.write('<NO INVARIANTS INFERRED>')


# one pass template
# FIXME: Daikon is very failure-prone; work around with it
def one_pass(junit_path, agent_path, go, this_hash, target_set):
    os.sys_call("git checkout " + this_hash)
    os.sys_call("mvn clean")
    
    bin_path = mvn.path_from_mvn_call("outputDirectory")
    test_bin_path = mvn.path_from_mvn_call("testOutputDirectory")
    cp = mvn.full_classpath(junit_path, bin_path, test_bin_path)
    print "\n===full classpath===\n" + cp + "\n"
    
    java_cmd = "java -cp " + cp
    
    os.sys_call("mvn test -DskipTests")
    junit_torun = mvn.junit_torun_str()
    print "\n===junit torun===\n" + junit_torun + "\n"
    
    #### dynamic run one round for all information    
    prefixes = daikon.common_prefixes(target_set)
    prefix_regexes = []
    for p in prefixes:
        prefix_regexes.append(p + "*")
    instrument_regex = "|".join(prefix_regexes)
    print "\n===instrumentation pattern===\n" + instrument_regex + "\n"
    # run tests with instrumentation
    run_instrumented_tests = \
        " ".join([java_cmd, 
                  "-javaagent:" + agent_path + "=\"" + instrument_regex + "\"",
                  junit_torun])
    print "\n=== Instrumented testing command to run: \n" + run_instrumented_tests
    os.sys_call(run_instrumented_tests, ignore_bad_exit=True)
    dyncg_file = go + "_getty_dyncg_-hash-_.ex"
    os.update_file_hash(dyncg_file, this_hash)
    dynfg_file = go + "_getty_dynfg_-hash-_.ex"
    os.update_file_hash(dynfg_file, this_hash)
    ####
    
    # add test methods into target set
    _, callee_of = agency.caller_callee(go, this_hash)
    all_tests = junit_torun.split(" ")[1:]
    for possible_test_mtd in callee_of.keys():
        for one_test in all_tests:
            if possible_test_mtd.startswith(one_test):
                target_set.add(possible_test_mtd)
    
    select_pattern = daikon.reformat_all(target_set, more_ppts=True)
    print "\n===select pattern===\n" + select_pattern + "\n"
    
    # run Chicory for trace
    run_chicory = \
        " ".join([java_cmd, "daikon.Chicory --exception-handling", \
                  "--dtrace-file="+rel_go(go)+"_getty_trace_"+this_hash+"_.dtrace.gz", \
                  "--ppt-select-pattern=\'"+select_pattern+"\'", \
                  junit_torun])
    print "\n=== Daikon:Chicory command to run: \n" + run_chicory
    os.sys_call(run_chicory, ignore_bad_exit=True)
    
    # run Daikon for invariants
    for tgt in target_set:
        run_daikon = \
            " ".join([java_cmd, "daikon.Daikon", 
                      go+"_getty_trace_"+this_hash+"_.dtrace.gz", \
                      "--ppt-select-pattern=\'"+daikon.dfformat(tgt, more_ppts=True)+"\'", \
                      "--no_text_output --show_progress", \
                      "-o", go+"_getty_inv__"+daikon.fsformat(tgt)+"__"+this_hash+"_.inv.gz"])
        print "\n=== Daikon:Daikon command to run: \n" + run_daikon
        os.sys_call(run_daikon, ignore_bad_exit=True)
    
    # run PrintInvariants for analysis
    for tgt in target_set:
        target_ff = daikon.fsformat(tgt)
        run_printinv = \
            " ".join([java_cmd, "daikon.PrintInvariants", \
                      "--ppt-select-pattern=\'"+daikon.dfformat(tgt)+"\'", \
                      go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.gz"])
        out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.txt"
        print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
        os.sys_call(run_printinv + " > " + out_file, ignore_bad_exit=True)
        sort_txt_inv(out_file)
    
    git.clear_temp_checkout(this_hash)


# the main entrance
def visit(junit_path, agent_path, go, prev_hash, post_hash, targets):
    
#     # DEBUG ONLY
#     print common_prefixes(old_all_methods)
#     print reformat_all(common_prefixes(old_all_methods))
#     print common_prefixes(new_all_methods)
#     print reformat_all(common_prefixes(new_all_methods))
    
    print("\n****************************************************************");
    print("        Getty Center: Semantiful Differential Analyzer");
    print("****************************************************************\n");
    
    '''
        1-st pass: checkout prev_commit as detached head, and get invariants for all interesting targets
    '''
    one_pass(junit_path, agent_path, go, prev_hash, targets)
    
    '''
        2-nd pass: checkout post_commit as detached head, and get invariants for all interesting targets
    '''
    one_pass(junit_path, agent_path, go, post_hash, targets)
    
    print 'Center analysis is completed.'
