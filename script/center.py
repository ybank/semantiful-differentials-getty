# all Daikon's usage for invariant analysis

from misc import *
from utils import *


# relative path of getty output path (go), when pwd is root dir of project
def rel_go(go):
    if go.endswith("/"):
        go = go[:-1]
    lsi = go.rfind("/")
    return ".." + go[lsi:] + "/"


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
    select_pattern = reformat_all(common_prefixes(target_set), more_ppts=True)
    print "\n===select pattern===\n" + select_pattern + "\n"
    
    # run Chicory for trace
    run_chicory = \
        " ".join([java_cmd, "daikon.Chicory", \
                  "--dtrace-file="+rel_go(go)+"_getty_trace_"+this_hash+"_.dtrace.gz", \
                  "--ppt-select-pattern=\'"+select_pattern+"\'", \
                  junit_torun])
    print "=== Daikon:Chicory command to run: \n" + run_chicory
    sys_call(run_chicory, ignore_bad_exit=True)
    
    # run Daikon for invariants
    for tgt in target_set:
        run_daikon = \
            " ".join([java_cmd, "daikon.Daikon", 
                      go+"_getty_trace_"+this_hash+"_.dtrace.gz", \
                      "--ppt-select-pattern=\'"+dfformat(tgt, more_ppts=True)+"\'", \
                      "--no_text_output --show_progress", \
                      "-o", go+"_getty_inv__"+fsformat(tgt)+"__"+this_hash+"_.inv.gz"])
        print "=== Daikon:Daikon command to run: \n" + run_daikon
        sys_call(run_daikon, ignore_bad_exit=True)
    
    # run PrintInvariants for analysis
    for tgt in target_set:
        run_printinv = \
            " ".join([java_cmd, "daikon.PrintInvariants", \
                      "--ppt-select-pattern=\'"+dfformat(tgt)+"\'", \
                      go+"_getty_inv__"+fsformat(tgt)+"__"+this_hash+"_.inv.gz"])
        print "=== Daikon:PrintInvs command to run: \n" + run_printinv
        sys_call(run_printinv, ignore_bad_exit=True)
    
    clear_temp_checkout(this_hash)


# the main entrance
def visit(junit_path, \
          go, prev_hash, post_hash, \
          old_changed_methods, \
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
        1-st pass: checkout prev_commit as detached head, and get invariants for all interesting target
    '''
    one_pass(junit_path, go, prev_hash, old_changed_methods)
    
    '''
        2-nd pass: checkout post_commit as detached head, and get invariants for all interesting target
    '''
#     one_pass(junit_path, go, post_hash, new_improved_changed_methods)
    
    print 'Center analysis is completed.'
