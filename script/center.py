# all Daikon's usage for invariant analysis

import re

from misc import *
from utils import *


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
                elif re.match(".*:::(ENTER|EXIT|CLASS|OBJECT).*", line):
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


# one pass template
# FIXME: Daikon is very failure-prone; work around with it
def one_pass(junit_path, go, this_hash, target_set):
    sys_call("git checkout " + this_hash)
    
    bin_path = path_from_mvn_call("outputDirectory")
    test_bin_path = path_from_mvn_call("testOutputDirectory")
    cp = full_classpath(junit_path, bin_path, test_bin_path)
    print "\n===full classpath===\n" + cp + "\n"
    
    sys_call("mvn test -DskipTests")
    junit_torun = junit_torun_str()
    print "\n===junit torun===\n" + junit_torun + "\n"
    
    java_cmd = "java -cp " + cp
    select_pattern = reformat_all(target_set, more_ppts=True)
    print "\n===select pattern===\n" + select_pattern + "\n"
    
    # run Chicory for trace
    run_chicory = \
        " ".join([java_cmd, "daikon.Chicory", \
                  "--dtrace-file="+rel_go(go)+"_getty_trace_"+this_hash+"_.dtrace.gz", \
                  "--ppt-select-pattern=\'"+select_pattern+"\'", \
                  junit_torun])
    print "\n=== Daikon:Chicory command to run: \n" + run_chicory
    sys_call(run_chicory, ignore_bad_exit=True)
    
    # run Daikon for invariants
    for tgt in target_set:
        run_daikon = \
            " ".join([java_cmd, "daikon.Daikon", 
                      go+"_getty_trace_"+this_hash+"_.dtrace.gz", \
                      "--ppt-select-pattern=\'"+dfformat(tgt, more_ppts=True)+"\'", \
                      "--no_text_output --show_progress", \
                      "-o", go+"_getty_inv__"+fsformat(tgt)+"__"+this_hash+"_.inv.gz"])
        print "\n=== Daikon:Daikon command to run: \n" + run_daikon
        sys_call(run_daikon, ignore_bad_exit=True)
    
    # run PrintInvariants for analysis
    for tgt in target_set:
        target_ff = fsformat(tgt)
        run_printinv = \
            " ".join([java_cmd, "daikon.PrintInvariants", \
                      "--ppt-select-pattern=\'"+dfformat(tgt)+"\'", \
                      go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.gz"])
        out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.txt"
        print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
        sys_call(run_printinv + " > " + out_file, ignore_bad_exit=True)
        sort_txt_inv(out_file)
    
    clear_temp_checkout(this_hash)


# the main entrance
def visit(junit_path, \
          go, prev_hash, post_hash, \
          old_changed_methods, old_improved_changed_methods, old_added_changed_methods, \
          old_all_callers, old_all_cccs, old_all_methods, \
          new_changed_methods, new_improved_changed_methods, new_removed_changed_methods, \
          new_all_callers, new_all_cccs, new_all_methods):
    
#     # DEBUG ONLY
#     print common_prefixes(old_all_methods)
#     print reformat_all(common_prefixes(old_all_methods))
#     print common_prefixes(new_all_methods)
#     print reformat_all(common_prefixes(new_all_methods))
    
    print("\n*************************************************************");
    print("Getty Center: Semantiful Differential Analyzer");
    print("*************************************************************\n");
    
    '''
        1-st pass: checkout prev_commit as detached head, and get invariants for all interesting targets
    '''
    one_pass(junit_path, go, prev_hash, set(old_improved_changed_methods + old_all_callers))
    
    '''
        2-nd pass: checkout post_commit as detached head, and get invariants for all interesting targets
    '''
    one_pass(junit_path, go, post_hash, set(new_improved_changed_methods + new_all_callers))
    
    print 'Center analysis is completed.'
