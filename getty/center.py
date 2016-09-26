# all Daikon's usage for invariant analysis

import re
import sys
from functools import partial
from multiprocessing import Pool
from os import path, makedirs

import agency
import config
from tools import daikon, git, html, mvn, os, profiler


SHOW_DEBUG_INFO = config.show_debug_info
SHOW_MORE_DEBUG_INFO = config.show_debug_details


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
#         out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.out"
#         print "\n=== Daikon:PrintInvs command to run: \n" + run_printinv
#         os.sys_call(run_printinv + " > " + out_file, ignore_bad_exit=True)
#         sort_txt_inv(out_file)

# v4. flexible to be run in parallel, in daikon-online mode
def seq_get_invs(target_set_index_pair, java_cmd, junit_torun, go, this_hash):
    index = target_set_index_pair[1]
    target_set = target_set_index_pair[0]
    print "\n\t****\n" + "  forked: " + index + "\n\t****\n"
    
#     select_pattern = daikon.select_full(target_set)
    select_pattern = daikon.dfformat_full_ordered(target_set)
    print "\n===select pattern===\n" + select_pattern + "\n"
    
    inv_gz = go + "_getty_inv_" + this_hash + "_." + index
    if config.compress_inv:
        inv_gz += ".inv.gz"
    else:
        inv_gz += ".inv"
    
    daikon_control_opt_list = []
    if SHOW_MORE_DEBUG_INFO:
        daikon_control_opt_list.append("--show_progress --no_text_output")
    elif SHOW_DEBUG_INFO:
        daikon_control_opt_list.append("--no_show_progress --no_text_output")
    else:
        daikon_control_opt_list.append("--no_text_output")
    if config.disable_known_invs:
        daikon_control_opt_list.append("--disable-all-invariants")
    if config.omit_redundant_invs:
        daikon_control_opt_list.append("--omit_from_output 0r")
    if config.daikon_format_only:
        daikon_control_opt_list.append("--format Daikon")
    daikon_control_opt_list.append(config.blacked_daikon_invs_exp)
    daikon_display_args = " ".join(daikon_control_opt_list)
    # run Chicory + Daikon (online) for invariants without trace I/O
    run_chicory_daikon = \
        " ".join([java_cmd, "daikon.Chicory --daikon-online --exception-handling", \
                  "--daikon-args=\""+daikon_display_args, \
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
        out_file = go+"_getty_inv__"+target_ff+"__"+this_hash+"_.inv.out"
        run_printinv = \
            " ".join([java_cmd, "daikon.PrintInvariants", "--format Daikon", \
                      "--ppt-select-pattern=\'"+daikon.dfformat(tgt)+"\'", \
                      "--output", out_file, inv_gz])
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
    os.remove_file(inv_gz)


# one pass template
def one_info_pass(
        junit_path, sys_classpath, agent_path, cust_mvn_repo, dyng_go, go, this_hash, target_set,
        changed_methods, changed_tests, inner_dataflow_methods, outer_dataflow_methods):
    os.sys_call("git checkout " + this_hash)
    os.sys_call("mvn clean")
    
    bin_path = mvn.path_from_mvn_call("outputDirectory")
    test_bin_path = mvn.path_from_mvn_call("testOutputDirectory")
    cp = mvn.full_classpath(junit_path, sys_classpath, bin_path, test_bin_path)
    if SHOW_DEBUG_INFO:
        print "\n===full classpath===\n" + cp + "\n"
    
    print "\ncopying all code to specific directory ...\n"
    all_code_dirs = [mvn.path_from_mvn_call("sourceDirectory"),
                     # mvn.path_from_mvn_call("scriptSourceDirectory"),
                     mvn.path_from_mvn_call("testSourceDirectory")]
    getty_code_store = go + '_getty_allcode_' + this_hash + '_/'
    makedirs(getty_code_store)
    for adir in all_code_dirs:
        os.sys_call(" ".join(["cp -r", adir + "/*", getty_code_store]), ignore_bad_exit=True)
    
    if config.use_special_junit_for_dyn:
        info_junit_path = os.rreplace(junit_path, config.default_junit_version, config.special_junit_version, 1)
        infocp = mvn.full_classpath(info_junit_path, sys_classpath, bin_path, test_bin_path)
    else:
        infocp = cp
    java_cmd = " ".join(["java", "-cp", infocp, 
#                          "-Xms"+config.min_heap, 
                         "-Xmx"+config.max_heap, 
                         "-XX:+UseConcMarkSweepGC", 
#                          "-XX:-UseGCOverheadLimit",
                         "-XX:-UseSplitVerifier",  # FIXME: JDK 8- only! 
                         ])
    
    # os.sys_call("mvn test -DskipTests", ignore_bad_exit=True)
    os.sys_call("mvn test-compile")
    
    junit_torun = mvn.junit_torun_str(cust_mvn_repo)
    if SHOW_DEBUG_INFO:
        print "\n===junit torun===\n" + junit_torun + "\n"
    
    #### dynamic run one round for all information    
    prefixes = daikon.common_prefixes(target_set)
    common_package = ''
    if len(prefixes) == 1:
        last_period_index = prefixes[0].rindex('.')
        if last_period_index > 0:
            # the common package should be at least one period away from the rest
            common_package = prefixes[0][:last_period_index]
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
    
    if not path.exists(dyng_go):
        makedirs(dyng_go)
    os.sys_call(run_instrumented_tests, ignore_bad_exit=True)

    os.merge_dyn_files(dyng_go, go, "_getty_dyncg_-hash-_.ex", this_hash)
    os.merge_dyn_files(dyng_go, go, "_getty_dynfg_-hash-_.ex", this_hash)
    
    caller_of, callee_of = agency.caller_callee(go, this_hash)
    pred_of, succ_of = agency.pred_succ(go, this_hash)
    
    # add test methods into target set
    test_set = agency.get_test_set_dyn(target_set, callee_of, junit_torun)
    
    # set target set here
    refined_target_set = \
        agency.refine_targets(target_set, test_set,
                              caller_of, callee_of, pred_of, succ_of,
                              changed_methods, changed_tests, 
                              inner_dataflow_methods, outer_dataflow_methods)
        
    profiler.log_csv(["method_count", "test_count", "refined_target_count"],
                     [[len(target_set), len(test_set), len(refined_target_set)]], 
                     go + "_getty_y_method_count_" + this_hash + "_.profile.readable")
    
    git.clear_temp_checkout(this_hash)
    
    return common_package, test_set, refined_target_set, cp, junit_torun


# one pass template
def one_inv_pass(go, cp, junit_torun, this_hash, refined_target_set, analysis_only=False):
    if not analysis_only:
        os.sys_call("git checkout " + this_hash)
    
    os.sys_call("mvn clean")
    
    if SHOW_DEBUG_INFO:
        print "\n===full classpath===\n" + cp + "\n"
    
    java_cmd = " ".join(["java", "-cp", cp, 
#                          "-Xms"+config.min_heap, 
                         "-Xmx"+config.max_heap, 
                         "-XX:+UseConcMarkSweepGC", 
#                          "-XX:-UseGCOverheadLimit",
                         "-XX:-UseSplitVerifier",  # FIXME: JDK 8- only! 
                         ])
    
    # os.sys_call("mvn test -DskipTests", ignore_bad_exit=True)
    os.sys_call("mvn test-compile")
    
    if SHOW_DEBUG_INFO:
        print "\n===junit torun===\n" + junit_torun + "\n"
    
    # v3.2, v4 execute with 4 core
    num_primary_workers = config.num_master_workers
    auto_parallel_targets = config.auto_fork
    slave_load = config.classes_per_fork
    
    target_map = daikon.target_s2m(refined_target_set)
    all_classes = target_map.keys()
    
    if len(refined_target_set) <= num_primary_workers or (num_primary_workers == 1 and not auto_parallel_targets):
        single_set_tuple = (refined_target_set, "0")
        seq_get_invs(single_set_tuple, java_cmd, junit_torun, go, this_hash)
    elif num_primary_workers > 1:  # FIXME: this distributation is buggy
        target_set_inputs = []
        all_target_set_list = list(refined_target_set)
        each_bulk_size = int(len(refined_target_set) / num_primary_workers)
        
        seq_func = partial(seq_get_invs, 
                           java_cmd=java_cmd, junit_torun=junit_torun, go=go, this_hash=this_hash)
        for i in range(num_primary_workers):
            if not(i == num_primary_workers - 1):
                sub_list_tuple = (all_target_set_list[each_bulk_size*i:each_bulk_size*(i+1)], str(i))                
                target_set_inputs.append(sub_list_tuple)
            else:
                sub_list_tuple = (all_target_set_list[each_bulk_size*i:], str(i))
                target_set_inputs.append(sub_list_tuple)
        input_pool = Pool(num_primary_workers)
        input_pool.map(seq_func, target_set_inputs)
        input_pool.close()
        input_pool.join()
    elif num_primary_workers == 1 and auto_parallel_targets and slave_load >= 1:
        # elastic automatic processing
        target_set_inputs = []
        num_processes = 0
        
        # target_map has been calculated already
        # target_map = daikon.target_s2m(refined_target_set)
        # all_classes = target_map.keys()
        num_keys = len(all_classes)
        seq_func = partial(seq_get_invs, 
                           java_cmd=java_cmd, junit_torun=junit_torun, go=go, this_hash=this_hash)
        
        for i in range(0, num_keys, slave_load):
            # (inclusive) lower bound is i
            # (exclusive) upper bound:
            j = min(i+slave_load, num_keys)
            sublist = []
            for k in range(i, j):
                the_key = all_classes[k]
                sublist.append(the_key)  # so it won't miss class/object invariants
                sublist += target_map[the_key]
            sublist_tuple = (sublist, str(num_processes))
            target_set_inputs.append(sublist_tuple)
            num_processes += 1
        
        max_parallel_processes = config.num_slave_workers
        if not analysis_only:
            profiler.log_csv(["class_count", "process_count", "max_parallel_processes", "slave_load"],
                             [[num_keys, num_processes, max_parallel_processes, slave_load]],
                             go + "_getty_y_elastic_count_" + this_hash + "_.profile.readable")
        
        input_pool = Pool(max_parallel_processes)
        input_pool.map(seq_func, target_set_inputs)
        input_pool.close()
        input_pool.join()
        
    else:
        print "\nIncorrect option for one center pass:"
        print "\tnum_primary_workers:", str(num_primary_workers)
        print "\tauto_parallel_targets:", str(auto_parallel_targets)
        print "\tslave_load", str(slave_load)
        sys.exit(1)
    
    if config.compress_inv:
        os.remove_many_files(go, "*.inv.gz")
    else:
        os.remove_many_files(go, "*.inv")
    
    # include coverage report for compare
    if config.analyze_test_coverage and not analysis_only:
        try:
            mvn.generate_coverage_report(go, this_hash)
        except:
            pass
    
    if not analysis_only:
        git.clear_temp_checkout(this_hash)
    
    return all_classes


def mixed_passes(go, refined_target_set, prev_hash, post_hash,
                 old_cp, new_cp, old_junit_torun, new_junit_torun):
    # checkout old commit, then checkout new tests
    os.sys_call("git checkout " + prev_hash)
    new_test_path = mvn.path_from_mvn_call("testSourceDirectory")
    os.sys_call(" ".join(["git", "checkout", post_hash, new_test_path]))
#     # may need to check whether it is compilable, return code?
#     os.sys_call("mvn clean test-compile")
    one_inv_pass(go, new_cp, new_junit_torun,
                 prev_hash + "_" + post_hash,
                 refined_target_set, analysis_only=True)
    git.clear_temp_checkout(prev_hash)
    
    # checkout old commit, then checkout new src
    os.sys_call("git checkout " + prev_hash)
    new_src_path = mvn.path_from_mvn_call("sourceDirectory")
    os.sys_call(" ".join(["git", "checkout", post_hash, new_src_path]))
#     # may need to check whether it is compilable, return code?
#     os.sys_call("mvn clean test-compile")
    one_inv_pass(go, new_cp, old_junit_torun,
                 post_hash + "_" + prev_hash,
                 refined_target_set, analysis_only=True)
    git.clear_temp_checkout(prev_hash)
    

# the main entrance
def visit(junit_path, sys_classpath, agent_path, cust_mvn_repo, separate_go, prev_hash, post_hash, targets, iso,
          old_changed_methods, old_changed_tests, old_inner_dataflow_methods, old_outer_dataflow_methods,
          new_changed_methods, new_changed_tests, new_inner_dataflow_methods, new_outer_dataflow_methods):
    
    dyng_go = separate_go[0]
    go = separate_go[1]
    
    print("\n****************************************************************");
    print("        Getty Center: Semantiful Differential Analyzer            ");
    print("****************************************************************\n");
    
    '''
        1-st pass: checkout prev_commit as detached head, and get new interested targets
    '''
    old_common_package, old_test_set, old_refined_target_set, old_cp, old_junit_torun = \
        one_info_pass(
            junit_path, sys_classpath, agent_path, cust_mvn_repo, dyng_go, go, prev_hash, targets,
            old_changed_methods, old_changed_tests, old_inner_dataflow_methods, old_outer_dataflow_methods)
    
    '''
        2-nd pass: checkout post_commit as detached head, and get new interested targets
    '''
    new_common_package, new_test_set, new_refined_target_set, new_cp, new_junit_torun = \
        one_info_pass(
            junit_path, sys_classpath, agent_path, cust_mvn_repo, dyng_go, go, post_hash, targets,
            new_changed_methods, new_changed_tests, new_inner_dataflow_methods, new_outer_dataflow_methods)
    
    '''
        middle pass: set common interests
    '''
    refined_target_set = old_refined_target_set | new_refined_target_set
    if config.analyze_tests:
        refined_target_set = refined_target_set | set(old_changed_tests) | set(new_changed_tests)
    
    html.src_to_html(refined_target_set, go, prev_hash)
    html.src_to_html(refined_target_set, go, post_hash)
    
    '''
        3-rd pass: checkout prev_commit as detached head, and get invariants for all interesting targets
    '''
    old_all_classes = one_inv_pass(go,
        old_cp, old_junit_torun, prev_hash, refined_target_set)
    
    '''
        4-th pass: checkout post_commit as detached head, and get invariants for all interesting targets
    '''
    new_all_classes = one_inv_pass(go,
        new_cp, new_junit_torun, post_hash, refined_target_set)

    '''
        more passes: checkout mixed commits as detached head, and get invariants for all interesting targets
    '''
    if iso:
        mixed_passes(go, refined_target_set, prev_hash, post_hash,
                     old_cp, new_cp, old_junit_torun, new_junit_torun)
    
    '''
        prepare to return
    '''
    all_classes_set = set(old_all_classes + new_all_classes)
    common_package = ''
    if old_common_package != '' and new_common_package != '':
        if (len(old_common_package) < len(new_common_package) and 
                (new_common_package+'.').find(old_common_package+'.') == 0):
            common_package = old_common_package
        elif (len(old_common_package) >= len(new_common_package) and 
                (old_common_package+'.').find(new_common_package+'.') == 0):
            common_package = old_common_package
    
    print 'Center analysis is completed.'
    return common_package, all_classes_set, refined_target_set, \
        old_test_set, old_refined_target_set, new_test_set, new_refined_target_set
