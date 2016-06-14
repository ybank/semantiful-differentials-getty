# all Daikon's usage for invariant analysis

import re
from functools import partial
from multiprocessing import Pool

import agency
from tools import daikon, git, mvn, os, profiler


SHOW_DEBUG_INFO = True
SHOW_MORE_DEBUG_INFO = False


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


# Chicory-Daikon-Invariant
# # v3. flexible to be run in parallel
# def seq_get_invs(target_set, java_cmd, junit_torun, go, this_hash):
#     index = target_set[-1]
#     target_set = target_set[:-1]
#     
#     select_pattern = daikon.reformat_all(target_set, more_ppts=True)
#     print "\n===select pattern===\n" + select_pattern + "\n"
#     
#     run_chicory = \
#         " ".join([java_cmd, "daikon.Chicory --exception-handling", \
#                   "--dtrace-file="+rel_go(go)+"_getty_trace_"+this_hash+"_."+index+".dtrace.gz", \
#                   "--ppt-select-pattern=\'"+select_pattern+"\'", \
#                   junit_torun])
#     print "\n=== Daikon:Chicory command to run: \n" + run_chicory
#     os.sys_call(run_chicory, ignore_bad_exit=True)
#     
#     run_daikon = \
#         " ".join([java_cmd, "daikon.Daikon", 
#                   go+"_getty_trace_"+this_hash+"_."+index+".dtrace.gz", \
#                   "--ppt-select-pattern=\'"+daikon.dfformat_full(target_set)+"\'", \
#                   "--no_text_output", "--show_progress", \
#                   "-o", go+"_getty_inv_"+this_hash+"_."+index+".inv.gz"])
#     print "\n=== Daikon:Daikon command to run: \n" + run_daikon
#     os.sys_call(run_daikon, ignore_bad_exit=True)
#     
#     os.remove_file(go+"_getty_trace_"+this_hash+"_."+index+".dtrace.gz")
#     
#     for tgt in target_set:
#         target_ff = daikon.fsformat(tgt)
#         run_printinv = \
#             " ".join([java_cmd, "daikon.PrintInvariants", \
#                       "--ppt-select-pattern=\'"+daikon.dfformat(tgt)+"\'", \
#                       go+"_getty_inv_"+this_hash+"_."+index+".inv.gz"])
#         out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.txt"
#         print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
#         os.sys_call(run_printinv + " > " + out_file, ignore_bad_exit=True)
#         sort_txt_inv(out_file)

# v4. flexible to be run in parallel, in daikon-online mode
def seq_get_invs(target_set, java_cmd, junit_torun, go, this_hash):
    index = target_set[-1]
    target_set = target_set[:-1]
    
    select_pattern = daikon.select_full(target_set)
    print "\n===select pattern===\n" + select_pattern + "\n"
    
    inv_gz = go + "_getty_inv_" + this_hash + "_." + index + ".inv.gz"
    
    # run Chicory + Daikon (online) for invariants without trace I/O
    run_chicory_daikon = \
        " ".join([java_cmd, "daikon.Chicory --daikon-online --exception-handling", \
                  "--daikon-args=\"--show_progress --no_text_output", \
                  "-o", inv_gz+"\"", \
                  "--ppt-select-pattern=\""+select_pattern+"\"", \
                  junit_torun])
    if SHOW_DEBUG_INFO:
        print "\n=== Daikon:Chicory+Daikon(online) command to run: \n" + run_chicory_daikon
    os.sys_call(run_chicory_daikon, ignore_bad_exit=True)
        
#     # run Chicory for trace
#     run_chicory = \
#         " ".join([java_cmd, "daikon.Chicory --exception-handling", \
#                   "--dtrace-file="+rel_go(go)+"_getty_trace_"+this_hash+"_."+index+".dtrace.gz", \
#                   "--ppt-select-pattern=\""+select_pattern+"\"", \
#                   junit_torun])
#     if SHOW_DEBUG_INFO:
#         print "\n=== Daikon:Chicory command to run: \n" + run_chicory
#     os.sys_call(run_chicory, ignore_bad_exit=True)
#     
#     # run Daikon for invariants
#     run_daikon = \
#         " ".join([java_cmd, "daikon.Daikon --show_progress --no_text_output", \
#                   go+"_getty_trace_"+this_hash+"_."+index+".dtrace.gz", \
#                   "-o", inv_gz+"\"", \
# #                   "--ppt-select-pattern=\""+select_pattern+"\"", \
#                   junit_torun])
#     if SHOW_DEBUG_INFO:
#         print "\n=== Daikon:Daikon command to run: \n" + run_daikon
#     os.sys_call(run_daikon, ignore_bad_exit=True)
    if SHOW_DEBUG_INFO:
        current_count = 0
        total_count = len(target_set)
    for tgt in target_set:
        target_ff = daikon.fsformat(tgt)
        out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.txt"
        run_printinv = \
            " ".join([java_cmd, "daikon.PrintInvariants", \
                      "--ppt-select-pattern=\'"+daikon.dfformat(tgt)+"\'", \
                      "--output", out_file, \
                      go+"_getty_inv_"+this_hash+"_."+index+".inv.gz"])
        if SHOW_DEBUG_INFO:
            current_count += 1
            os.print_progress(current_count, total_count, 
                              prefix='Progress('+index+'):', 
                              suffix='('+str(current_count)+'/'+str(total_count)+': '+tgt+')'+' '*20, 
                              bar_length=50)
        elif SHOW_MORE_DEBUG_INFO:
            print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
        os.sys_call(run_printinv, ignore_bad_exit=True)
        sort_txt_inv(out_file)


# one pass template
def one_pass(junit_path, sys_classpath, agent_path, go, this_hash, target_set, 
             parallel_level=1, min_heap_size="2048m", max_heap_size="16384m"):
    os.sys_call("git checkout " + this_hash)
    os.sys_call("mvn clean")
    
    bin_path = mvn.path_from_mvn_call("outputDirectory")
    test_bin_path = mvn.path_from_mvn_call("testOutputDirectory")
    cp = mvn.full_classpath(junit_path, sys_classpath, bin_path, test_bin_path)
    if SHOW_DEBUG_INFO:
        print "\n===full classpath===\n" + cp + "\n"
    
    java_cmd = " ".join(["java", "-cp", cp, 
                         "-Xms"+min_heap_size, "-Xmx"+max_heap_size, "-XX:+UseConcMarkSweepGC"])
    
    os.sys_call("mvn test -DskipTests")
    junit_torun = mvn.junit_torun_str()
    if SHOW_DEBUG_INFO:
        print "\n===junit torun===\n" + junit_torun + "\n"
    
    #### dynamic run one round for all information    
    prefixes = daikon.common_prefixes(target_set)
    prefix_regexes = []
    for p in prefixes:
        prefix_regexes.append(p + "*")
    instrument_regex = "|".join(prefix_regexes)
    if SHOW_DEBUG_INFO:
        print "\n===instrumentation pattern===\n" + instrument_regex + "\n"
    # run tests with instrumentation
    run_instrumented_tests = \
        " ".join([java_cmd, 
                  "-javaagent:" + agent_path + "=\"" + instrument_regex + "\"",
                  junit_torun])
    if SHOW_DEBUG_INFO:
        print "\n=== Instrumented testing command to run: \n" + run_instrumented_tests
    os.sys_call(run_instrumented_tests, ignore_bad_exit=True)
    dyncg_file = go + "_getty_dyncg_-hash-_.ex"
    os.update_file_hash(dyncg_file, this_hash)
    dynfg_file = go + "_getty_dynfg_-hash-_.ex"
    os.update_file_hash(dynfg_file, this_hash)
    ####
    
    # add test methods into target set
    test_set = set()
    mtd_count = len(target_set)
    _, callee_of = agency.caller_callee(go, this_hash)
    all_tests = junit_torun.split(" ")[1:]
    for possible_test_mtd in callee_of.keys():
        if (not re.match(".*:((suite)|(setUp)|(tearDown))$", possible_test_mtd)):
            for one_test in all_tests:
                if possible_test_mtd.startswith(one_test):
                    test_set.add(possible_test_mtd)
    test_mtd_count = len(test_set)
    # set target set here
    target_set = target_set or test_set
    profiler.log_csv(["method_count", "test_count"], 
                     [[mtd_count, test_mtd_count]], 
                     go + "_getty_y_method_count_" + this_hash + "_.profile.readable")
    
#     select_pattern = daikon.reformat_all(target_set, more_ppts=True)
#     print "\n===select pattern===\n" + select_pattern + "\n"
#     
#     # run Chicory for trace
#     run_chicory = \
#         " ".join([java_cmd, "daikon.Chicory --exception-handling", \
#                   "--dtrace-file="+rel_go(go)+"_getty_trace_"+this_hash+"_.dtrace.gz", \
#                   "--ppt-select-pattern=\'"+select_pattern+"\'", \
#                   junit_torun])
#     print "\n=== Daikon:Chicory command to run: \n" + run_chicory
#     os.sys_call(run_chicory, ignore_bad_exit=True)
#     
# #     # run Daikon for invariants
# #     for tgt in target_set:
# #         run_daikon = \
# #             " ".join([java_cmd, "daikon.Daikon", 
# #                       go+"_getty_trace_"+this_hash+"_.dtrace.gz", \
# #                       "--ppt-select-pattern=\'"+daikon.dfformat(tgt, more_ppts=True)+"\'", \
# #                       "--no_text_output --show_progress", \
# #                       "-o", go+"_getty_inv__"+daikon.fsformat(tgt)+"__"+this_hash+"_.inv.gz"])
# #         print "\n=== Daikon:Daikon command to run: \n" + run_daikon
# #         os.sys_call(run_daikon, ignore_bad_exit=True)
# 
#     # run Daikon for invariants
#     # v2: use one big inv.gz file, from one dtrace file
#     run_daikon = \
#         " ".join([java_cmd, "daikon.Daikon", 
#                   go+"_getty_trace_"+this_hash+"_.dtrace.gz", \
#                   "--ppt-select-pattern=\'"+daikon.dfformat_full(target_set)+"\'", \
#                   "--no_text_output", "--show_progress", \
#                   "-o", go+"_getty_inv_"+this_hash+"_.inv.gz"])
#     print "\n=== Daikon:Daikon command to run: \n" + run_daikon
#     os.sys_call(run_daikon, ignore_bad_exit=True)
#
# #     # run PrintInvariants for analysis
# #     for tgt in target_set:
# #         target_ff = daikon.fsformat(tgt)
# #         run_printinv = \
# #             " ".join([java_cmd, "daikon.PrintInvariants", \
# #                       "--ppt-select-pattern=\'"+daikon.dfformat(tgt)+"\'", \
# #                       go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.gz"])
# #         out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.txt"
# #         print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
# #         os.sys_call(run_printinv + " > " + out_file, ignore_bad_exit=True)
# #         sort_txt_inv(out_file)
#         
#     # run PrintInvariants for analysis
#     # v2: get inv.txt from one big inv.gz file
#     for tgt in target_set:
#         target_ff = daikon.fsformat(tgt)
#         run_printinv = \
#             " ".join([java_cmd, "daikon.PrintInvariants", \
#                       "--ppt-select-pattern=\'"+daikon.dfformat(tgt)+"\'", \
#                       go+"_getty_inv_"+this_hash+"_.inv.gz"])
#         out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.txt"
#         print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
#         os.sys_call(run_printinv + " > " + out_file, ignore_bad_exit=True)
#         sort_txt_inv(out_file)

#     # v3.1 one core (purely sequential)
#     seq_get_invs(target_set, java_cmd, junit_torun, go, this_hash)
    
    # v3.2, v4 execute with 4 core
    if len(target_set) <= parallel_level:
        one_sublist = list(target_set)
        one_sublist.append("0")
        seq_get_invs(one_sublist, java_cmd, junit_torun, go, this_hash)
    else:
        target_set_inputs = []
        all_target_set_list = list(target_set)
        each_bulk_size = int(len(target_set) / parallel_level)
        
        seq_func = partial(seq_get_invs, 
                           java_cmd=java_cmd, junit_torun=junit_torun, go=go, this_hash=this_hash)
        for i in range(parallel_level):
            if not(i == parallel_level - 1):
                sub_list = all_target_set_list[each_bulk_size*i:each_bulk_size*(i+1)]
                sub_list.append(str(i))
                target_set_inputs.append(sub_list)
            else:
                sub_list = all_target_set_list[each_bulk_size*i:]
                sub_list.append(str(i))
                target_set_inputs.append(sub_list)
        input_pool = Pool(parallel_level)
        input_pool.map(seq_func, target_set_inputs)
        input_pool.close()
        input_pool.join()    
    
    target_set = target_set - test_set
    git.clear_temp_checkout(this_hash)


# the main entrance
def visit(junit_path, sys_classpath, agent_path, go, prev_hash, post_hash, targets,
          num_workers=4, min_heap="2048m", max_heap="16384m"):
    
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
    one_pass(junit_path, sys_classpath, agent_path, go, prev_hash, targets,
             parallel_level=num_workers, min_heap_size=min_heap, max_heap_size=max_heap)
    
    '''
        2-nd pass: checkout post_commit as detached head, and get invariants for all interesting targets
    '''
    one_pass(junit_path, sys_classpath, agent_path, go, post_hash, targets,
             parallel_level=num_workers, min_heap_size=min_heap, max_heap_size=max_heap)
    
    print 'Center analysis is completed.'
