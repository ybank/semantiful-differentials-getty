from utils import *


def visit(villa_path, pwd, go, prev_hash, post_hash, pkg_prefix="-"):
    
    print("\n*************************************************************");
    print("Getty Villa: Semantiful Differential Analyzer");
    print("*************************************************************\n");
    
    print "current working directory: " + pwd + "\n"
    
    diff_out = go + "text.diff"
    sys_call("git diff {0} {1} > {2}".format(prev_hash, post_hash, diff_out))
    
    '''
        1-st pass: checkout prev_commit as detached head, and get all sets and etc, in simple (bare) mode (-s)
            remember to clear after this pass
    '''
    sys_call("git checkout " + prev_hash)
    
    # src_path = path_from_mvn_call("sourceDirectory")
    bin_path = path_from_mvn_call("outputDirectory")
    test_src_rel_path = path_from_mvn_call("testSourceDirectory")
    if test_src_rel_path.startswith(pwd):
        test_src_rel_path = test_src_rel_path[len(pwd):]
    else:
        raise ValueError("pwd is not a prefix of test src path")
    print "current test src path (relative): " + test_src_rel_path + "\n"
    
    sys_call("mvn test -DskipTests")
    
    run_villa = "java -jar {0} -s {1} {2} {3} {4} {5} {6} -o {7}".format(
        villa_path, diff_out, bin_path, test_src_rel_path, pkg_prefix, prev_hash, post_hash, go)
    print "\n\nstart to run Villa ... \n\n" + run_villa
    sys_call(run_villa)
    
    old_changed_methods = read_str_from(go + "_getty_chgmtd_src_old_{0}_.ex".format(prev_hash))
    old_all_methods = read_str_from(go + "_getty_allmtd_src_{0}_.ex".format(prev_hash))
#     # DEBUG ONLY
#     print old_changed_methods
#     print len(old_all_methods)
    
    clear_temp_checkout(prev_hash)
    
    '''
        2-nd pass: checkout post_commit as detached head, and get all sets and etc, in complex mode (-c)
            remember to clear after this pass
    '''
    sys_call("git checkout " + post_hash)
    
    # src_path = path_from_mvn_call("sourceDirectory")
    bin_path = path_from_mvn_call("outputDirectory")
    test_src_rel_path = path_from_mvn_call("testSourceDirectory")
    if test_src_rel_path.startswith(pwd):
        test_src_rel_path = test_src_rel_path[len(pwd):]
    else:
        raise ValueError("pwd is not a prefix of test src path")
    print "current test src path (relative): " + test_src_rel_path + "\n"
    
    sys_call("mvn test -DskipTests")
    
    run_villa = "java -jar {0} -c {1} {2} {3} {4} {5} {6} -o {7}".format(
        villa_path, diff_out, bin_path, test_src_rel_path, pkg_prefix, prev_hash, post_hash, go)
    print "\n\nstart to run Villa ... \n\n" + run_villa
    sys_call(run_villa)
    
    new_changed_methods = read_str_from(go + "_getty_chgmtd_src_new_{0}_.ex".format(post_hash))
    new_improved_changed_methods = read_str_from(go + "_getty_chgmtd_src_{0}_{1}_.ex".format(prev_hash, post_hash))
    new_removed_changed_methods = read_str_from(go + "_getty_chgmtd_src_gone_{0}_{1}_.ex".format(prev_hash, post_hash))
    new_all_callers = read_str_from(go + "_getty_clr_{0}_.ex".format(post_hash))
    new_all_cccs = read_str_from(go + "_getty_ccc_{0}_.ex".format(post_hash))
    new_all_methods = read_str_from(go + "_getty_allmtd_src_{0}_.ex".format(post_hash))
#     # DEBUG ONLY
#     print new_changed_methods
#     print new_improved_changed_methods
#     print new_removed_changed_methods
#     print new_all_callers
#     print new_all_cccs
#     print len(new_all_methods)
    
    clear_temp_checkout(post_hash)
    
    '''
        3-rd pass: checkout prev_commit as detached head, and get all sets and etc, in recovery mode (-r)
            remember to clear after this pass
    '''
    sys_call("git checkout " + prev_hash)
    
    # src_path = path_from_mvn_call("sourceDirectory")
    bin_path = path_from_mvn_call("outputDirectory")
    test_src_rel_path = path_from_mvn_call("testSourceDirectory")
    if test_src_rel_path.startswith(pwd):
        test_src_rel_path = test_src_rel_path[len(pwd):]
    else:
        raise ValueError("pwd is not a prefix of test src path")
    print "current test src path (relative): " + test_src_rel_path + "\n"
    
    sys_call("mvn test -DskipTests")
    
    run_villa = "java -jar {0} -r {1} {2} {3} {4} {5} {6} -o {7}".format(
        villa_path, diff_out, bin_path, test_src_rel_path, pkg_prefix, prev_hash, post_hash, go)
    print "\n\nstart to run Villa ... \n\n" + run_villa
    sys_call(run_villa)
    
    old_improved_changed_methods = read_str_from(go + "_getty_chgmtd_src_{1}_{0}_.ex".format(prev_hash, post_hash))
    old_added_changed_methods = read_str_from(go + "_getty_chgmtd_src_gain_{0}_{1}_.ex".format(prev_hash, post_hash))
    old_all_callers = read_str_from(go + "_getty_clr_{0}_.ex".format(prev_hash))
    old_all_cccs = read_str_from(go + "_getty_ccc_{0}_.ex".format(prev_hash))
#     # DEBUG ONLY
#     print old_changed_methods
#     print old_improved_changed_methods
#     print old_added_changed_methods
#     print old_all_callers
#     print old_all_cccs
#     print len(old_all_methods)
    
    clear_temp_checkout(prev_hash)
    
    print 'Villa analysis is completed.'
    return old_changed_methods, old_improved_changed_methods, old_added_changed_methods, \
        old_all_callers, old_all_cccs, old_all_methods, \
        new_changed_methods, new_improved_changed_methods, new_removed_changed_methods, \
        new_all_callers, new_all_cccs, new_all_methods
