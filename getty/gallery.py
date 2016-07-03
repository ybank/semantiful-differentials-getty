from analysis.advisor import getty_append_report, report
from analysis.inspector import getty_csi_init, getty_csi_targets_prep
from tools.hdiff import diff_to_html, getty_append_semainfo
from tools.os import sys_call


def view(pwd, go, js_path, targets, new_all_cccs, prev_hash, post_hash, old_l2m, new_l2m):
    diff_in = pwd[:-1] + ".__getty_output__/text.diff"
    html_out = pwd[:-1] + ".__getty_output__/sema.diff.html"
    diff_to_html(diff_in, html_out, exclude_headers=False, old_l2m=old_l2m, new_l2m=new_l2m)
    getty_append_semainfo(html_out, targets, go, js_path, prev_hash, post_hash, old_l2m, new_l2m)
    report(targets, new_all_cccs, prev_hash, post_hash, go, js_path)
    getty_append_report(html_out)
    
    # open with Safari on Mac OS
    sys_call("open -a /Applications/Safari.app/Contents/MacOS/Safari " + html_out)
#     # open with default app
#     sys_call("open " + html_out)


def exam(pwd, go, js_path, common_package, all_classes_set,
         targets, new_refined_target_set, old_refined_target_set,
         new_modified_src, new_all_src,
         new_caller_of, new_callee_of, new_pred_of, new_succ_of,
         old_caller_of, old_callee_of, old_pred_of, old_succ_of,
         all_changed_tests, old_changed_tests, new_changed_tests,
         old_test_set, new_test_set,
         prev_hash, post_hash, old_l2m, new_l2m, old_m2l, new_m2l,
         view_results=True):
    
    refined_target_set = new_refined_target_set | old_refined_target_set
    refined_targets_parents_set = refined_target_set | all_classes_set
    
    diff_in = go + "text.diff"
    html_out = go + "sema.diff.html"
    diff_to_html(diff_in, html_out, exclude_headers=False, old_l2m=old_l2m, new_l2m=new_l2m)
    getty_append_semainfo(html_out, refined_targets_parents_set, go, js_path, prev_hash, post_hash, old_l2m, new_l2m)
    
    getty_csi_init(html_out)
    getty_csi_targets_prep(html_out, go, prev_hash, post_hash, common_package,
                           all_changed_tests, old_changed_tests, new_changed_tests,
                           new_modified_src, new_all_src,
                           old_test_set, new_test_set,
                           old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                           new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                           old_refined_target_set, new_refined_target_set, refined_target_set,
                           all_classes_set)
    
    if view_results:
        print 'opening rendered pages for review ...'
        # open with Safari on Mac OS
        # sys_call("open -a /Applications/Safari.app/Contents/MacOS/Safari " + html_out)
        # open with default app
        sys_call("open " + html_out)
