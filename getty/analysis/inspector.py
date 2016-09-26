# CSI inspection page section

import config
from analysis.solver import is_different, is_possibly_different
from tools.daikon import fsformat


def getty_csi_init(html_file, iso):
    with open(html_file, 'r+') as f:
        html_string = f.read()
        anchor = "<a href='#' id='getty-advice-title' onclick='return false;'>{{{__getty_advice__}}}</a>"
        isolation_ctrl = "<div id='csi-iso-ctrl' style='display:none;'><p>No Impact Isolation</p></div>\n"
        if iso:
            iso_links = ""
            for iso_type, iso_text, tcolor, tiptext in [
                        ("ni", "No Impact Isolation", "blue", "old src & tests\nvs.\nnew src & tests"),
                        ("si", "Source Change", "gray", "old src vs. new src\n(with same tests)"),
                        ("ti4o", "Test Change (for OLD Source)", "gray", "old tests vs. new tests\n(both for old src)"),
                        ("ti4n", "Test Change (for NEW Source)", "gray", "old tests vs. new tests\n(both for new src)")]:
                iso_links += \
                        "    <a id='csi-iso-link-" + iso_type + "' class='csi-iso-ctrl-group' href='#' " + \
                        " style='color: " + tcolor + ";' " + \
                        "onclick='return iso_type_reset(\"" + iso_type + "\");'><b>" + iso_text + "</b>" + \
                        "<span class='iso-type-tip'><pre>" + tiptext + "</pre></span></a>\n"
                if iso_type == "ni":
                    iso_links += "    <span id='iso-type-listing'>Invariant Changes Due To:</span>"
            isolation_ctrl = "<div id='csi-iso-ctrl' style='margin-top:10px;'>" + iso_links + "</div>\n"
        legends = "<div style='float:right;'>" + \
            "<span style='margin-left: 32px;'>Legends:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>" + \
            "<span><b><u>code-updated</u></b>&nbsp;&nbsp;&nbsp;</span>" + \
            "<span style='color:red;'>invariant-changed</span>&nbsp;&nbsp;&nbsp;" + \
            "<span style='color:gray;'>invariant-not-changed</span>&nbsp;&nbsp;&nbsp;" + \
            "<span>...(old-call-count + newly-added-calls)</span>&nbsp;&nbsp;" + \
            "</div>"
        html_string = html_string.replace(anchor,
            "<div id='csi-output-targets'></div>\n" + \
            "<div id='csi-output-neighbors-outer'>" + \
            "  <div id='csi-output-menu'>" + \
            "    <a href='#' id='whether-show-invequal' onclick='return toggle_show_invequal();'>Showing More Methods: YES</a>" + \
            "&nbsp;&nbsp;&nbsp;&nbsp;" + \
            "    <a href='#' id='whether-show-tests' onclick='return toggle_show_tests();'>Showing Tests: YES</a>" + \
            legends + \
            "  </div>\n" + \
            "  <div id='csi-output-neighbors' style='margin:8px;'>" + \
            "    <div style='text-align: center;'>" + \
            "Choose a method/class from above to show its invocation neighbors." + \
            "    </div>\n" + \
            "  </div>\n" + \
            "</div>\n" + \
            "<div id='csi-output-invcomp-outer'>" + isolation_ctrl + \
            "  <div id='csi-output-invcomp' style='margin: 8px 2px;'>" + \
            "    <div style='margin: 8px 4px; text-align: center;'>Invariant differentials will be shown here." + \
            "</div></div></div>")
        f.seek(0)
        f.truncate()
        f.write(html_string)


def __set_all_with_tests(new_all, map_of_map):
    for mtd in map_of_map:
        new_all.add(mtd)
        for m in map_of_map[mtd]:
            new_all.add(m)


def __link_to_show_neighbors(t, common_package, style_class=None):
    aid = "target-link-" + fsformat(t)
    cls = "target-linkstyle" + " class-" + aid
    if style_class is not None:
        cls += (" " + style_class)
    js_cmd = "return activateNeighbors(\"" + t + "\");"
    tname = t
    if common_package != '':
        tname = t[len(common_package)+1:]
    tname = tname.replace("<", "&lt;").replace(">", "&gt;")
    return "<a href='#' id='" + aid + "' class='" + cls + "' onclick='" + js_cmd + "'>" + tname + "</a>"


def __append_script_l2s(html_string, lst, for_whom):
    the_script = \
        for_whom + " = list_to_set([" + \
        ", ".join(["\"" + t + "\"" for t in lst]) + \
        "]);"
    place_holder = "</script>\n</body>"
    to_replace = "    " + the_script + "\n" + place_holder
    return html_string.replace(place_holder, to_replace)


def __append_script_mm2d(html_string, mm, for_whom):
    serialized = []
    for mtd in mm:
        serialized.append("\"" + mtd + "\"")
        value_entry = []
        for m in mm[mtd]:
            value_entry.append(m)
            value_entry.append(str(mm[mtd][m]))
        serialized.append(str(value_entry))
    the_script = \
        for_whom + " = list_list_to_dict_dict([" + \
        ", ".join(serialized) + "]);"
    place_holder = "</script>\n</body>"
    to_replace = "    " + the_script + "\n" + place_holder
    return html_string.replace(place_holder, to_replace)


def __append_script_common_package(html_string, common_package):
    if common_package != '' and common_package is not None:
        the_script = \
            "    " + "common_package = " + "\"" + common_package + "\";" + "\n" + \
            "    " + "common_prefix_length = " + str(len(common_package)+1) + ";" + "\n"
        place_holder = "</script>\n</body>"
        to_replace = the_script + place_holder
        return html_string.replace(place_holder, to_replace)
    else:
        return html_string


def _getty_csi_setvars(html_string, go, prev_hash, post_hash, common_package,
                       all_changed_tests, old_changed_tests, new_changed_tests,
                       new_modified_src, new_all_src,
                       old_test_set, new_test_set,
                       old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                       new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                       all_whose_inv_changed, all_whose_clsobj_inv_changed):
    html_string = __append_script_l2s(html_string, all_changed_tests, "all_changed_tests")
    html_string = __append_script_l2s(html_string, old_changed_tests, "old_changed_tests")
    html_string = __append_script_l2s(html_string, new_changed_tests, "new_changed_tests")
    
    new_all = set()
    __set_all_with_tests(new_all, new_caller_of)
    __set_all_with_tests(new_all, new_callee_of)
    __set_all_with_tests(new_all, new_pred_of)
    __set_all_with_tests(new_all, new_succ_of)
    html_string = __append_script_l2s(html_string, new_all, "all_project_methods")
    
    all_modified = set(all_changed_tests) | set(new_modified_src)
    html_string = __append_script_l2s(html_string, all_modified, "all_modified_targets")

    new_all_test_and_else = new_all - set(new_all_src)
    html_string = __append_script_l2s(html_string, new_all_test_and_else, "all_test_and_else")
    
    html_string = __append_script_l2s(html_string, all_whose_inv_changed, "all_whose_inv_changed")
    html_string = __append_script_l2s(html_string, all_whose_clsobj_inv_changed, "all_whose_clsobj_inv_changed")
    
#     # DEBUG ONLY
#     print new_caller_of
#     print new_callee_of
#     print new_pred_of
#     print new_succ_of
    
    html_string = __append_script_mm2d(html_string, old_caller_of, "prev_affected_caller_of")
    html_string = __append_script_mm2d(html_string, old_callee_of, "prev_affected_callee_of")
    html_string = __append_script_mm2d(html_string, old_pred_of, "prev_affected_pred_of")
    html_string = __append_script_mm2d(html_string, old_succ_of, "prev_affected_succ_of")
    html_string = __append_script_mm2d(html_string, new_caller_of, "post_affected_caller_of")
    html_string = __append_script_mm2d(html_string, new_callee_of, "post_affected_callee_of")
    html_string = __append_script_mm2d(html_string, new_pred_of, "post_affected_pred_of")
    html_string = __append_script_mm2d(html_string, new_succ_of, "post_affected_succ_of")
    
    html_string = __append_script_common_package(html_string, common_package)
    
    return html_string
    

def getty_csi_targets_prep(html_file, go, prev_hash, post_hash, common_package,
                           all_changed_tests, old_changed_tests, new_changed_tests,
                           new_modified_src, new_all_src,
                           old_test_set, new_test_set,
                           old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                           new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                           old_refined_target_set, new_refined_target_set, refined_target_set,
                           all_classes_set, iso):
    # TODO: 
    #   Consider to use new_refined_target_set, old_refined_target_set for better results
    
    all_whose_inv_changed = set()
    if config.analyze_tests and not config.limit_interest:
        all_considered = (set(new_all_src) | set(new_test_set))
    elif config.limit_interest:
        all_considered = refined_target_set
    else:
        all_considered = set(new_all_src)
    for mtd in all_considered:
        if iso:
            if is_possibly_different(mtd, go, prev_hash, post_hash):
                all_whose_inv_changed.add(mtd);
        else:
            if is_different(mtd, go, prev_hash, post_hash):
                all_whose_inv_changed.add(mtd);
    
    all_whose_clsobj_inv_changed = set()
    for cls in all_classes_set:
        if iso:
            if is_possibly_different(cls, go, prev_hash, post_hash):
                all_whose_clsobj_inv_changed.add(cls)
        else:
            if is_different(cls, go, prev_hash, post_hash):
                all_whose_clsobj_inv_changed.add(cls)

    with open(html_file, 'r') as rf:
        html_string = rf.read()
    targets_place_holder = "<div id='csi-output-targets'></div>"
    cpkg_disclaimer = ""
    if common_package != '' and common_package is not None:
        cpkg_disclaimer = "<h4 style='margin: 4px 0 8px 0'>Common Package: " + common_package + "</h4>"
    compare_commit_msgs = "<b>Compare Commits:</b> " + \
        "<a id='commit-msg-link' href='#'>" + prev_hash + " vs. " + post_hash + "</a>"
    replace_header = \
        "<div id='csi-output-targets'>" + compare_commit_msgs + cpkg_disclaimer + \
        "<h4 style='margin: 4px 0 8px 0'>Updated Source:</h4>"
    if new_modified_src:
        replacement = ", ".join([__link_to_show_neighbors(t, common_package) for t in new_modified_src])
    else:
        replacement = "<span>None</span>"
    embed_test_update = \
        "<br><br><h4 style='margin: 4px 0 8px 0'>Updated Tests:</h4>"
    if all_changed_tests:
        tests_replacement = ", ".join([__link_to_show_neighbors(t, common_package) for t in all_changed_tests])
    else:
        tests_replacement = "<span>None</span>"
    inv_change_update = \
        "<br><br><h4 style='margin: 4px 0 8px 0'>Invariant Changed:</h4>"
    if all_whose_inv_changed or all_whose_clsobj_inv_changed:
        if all_whose_inv_changed:
            invch_mtd_replacement = "<span>Methods: </span>" + ", ".join(
                [__link_to_show_neighbors(t, common_package, "output-invc-highlight") for t in all_whose_inv_changed])
        else:
            invch_mtd_replacement = "<span>Methods: None</span>"
        if all_whose_clsobj_inv_changed:
            invch_cls_replacement = "<span>Classes: </span>" + ", ".join(
                [__link_to_show_neighbors(t, common_package, "output-invc-highlight") for t in all_whose_clsobj_inv_changed])            
        else:
            invch_cls_replacement = "<span>Classes: None</span>"
        invch_replacement = invch_mtd_replacement + "<br>" + invch_cls_replacement
    else:
        invch_replacement = "<span>None</span>"
    replace_footer = "</div>"
    html_string = html_string.replace(targets_place_holder,
                                      replace_header + replacement + \
                                      embed_test_update + tests_replacement + \
                                      inv_change_update + invch_replacement + \
                                      replace_footer)

    html_string = _getty_csi_setvars(html_string, go, prev_hash, post_hash, common_package,
                                     all_changed_tests, old_changed_tests, new_changed_tests,
                                     new_modified_src, new_all_src,
                                     old_test_set, new_test_set,
                                     old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                                     new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                                     all_whose_inv_changed, all_whose_clsobj_inv_changed)
    
    with open(html_file, 'w') as wf:
        wf.write(html_string)
