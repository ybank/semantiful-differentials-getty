# CSI inspection page section

import config
from analysis.solver import is_different, is_possibly_different
from tools.daikon import fsformat_with_sigs, purify_target_name, simplify_target_name
from tools.html import create_show_hide_toggle, create_legends_tooltip


def getty_csi_init(html_file, iso):
    with open(html_file, 'r+') as f:
        html_string = f.read()
        anchor = "__getty_stub__"
        isolation_ctrl = "<div id='csi-iso-ctrl' style='display:none;'><p>No Impact Isolation</p></div>\n"
        if iso:
            iso_links = ""
            active_style = "color:blue;background:whitesmoke;"
            inactive_style = "color:gray;background:linear-gradient(whitesmoke, lightgray);"
            for iso_type, iso_text, link_style, tiptext in [
                    ("ni", "Source & Test Change", inactive_style, "old src & tests\nvs.\nnew src & tests"),
                    ("si", "Source Change Only", active_style, "old vs. new src\n(with same tests)"),
                    ("ti4o", "Test Change (for OLD Source)", inactive_style, "old tests vs. new tests\n(both for old src)"),
                    ("ti4n", "Test Change (for NEW Source)", inactive_style, "old tests vs. new tests\n(both for new src)")]:
                iso_links += \
                    "    <a id='csi-iso-link-" + iso_type + "' class='csi-iso-ctrl-group' href='#' " + \
                    " style='" + link_style + "' " + \
                    "onclick='return iso_type_reset(\"" + iso_type + "\");'>" + iso_text + \
                    "<span class='iso-type-tip'><pre>" + tiptext + "</pre></span></a>\n"
            iso_links = "<div class='link-button-tabs-bottom'>" + iso_links + "</div>"
            isolation_ctrl = "<div id='csi-iso-ctrl' style='margin-top:10px;'>\n" + \
                "    <span class='more-inv-display-option-listing menu-words'>Invariant Changes Due To:</span>\n" + \
                iso_links + "</div>\n"
        html_string = html_string.replace(anchor,
            "<div id='csi-output-targets'></div>\n" + \
            "<div id='csi-output-neighbors-outer'>" + \
            "  <div id='csi-output-menu' class='menu-words'>" + \
            "<span style='margin-right:4px;'>Methods without invariant changes </span>\n" + \
            "  " + create_show_hide_toggle("onoffswitch", "moremethodscb", "return toggle_show_invequal();") + "\n" + \
            "<span style='margin: 0px 4px 0 80px;'>Test cases </span>" + \
            "  " + create_show_hide_toggle("onoffswitch", "moretestscb", "return toggle_show_tests();") + "\n" + \
            "  " + create_legends_tooltip() + "\n" + \
            "  </div>\n" + \
            "  <div id='csi-output-neighbors' style='margin:8px;'>" + \
            "    <div style='text-align: center;'>" + \
            "Choose a method/class from above to show its invocation neighbors." + \
            "    </div>\n" + \
            "  </div>\n" + \
            "</div>\n" + \
            "<div id='csi-output-invcomp-outer'>\n" + isolation_ctrl + \
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


def __link_to_show_neighbors(t, common_package, all_codec_to_check=None, all_invc_to_check=None):
    aid = "target-link-" + fsformat_with_sigs(t)
    cls = "target-linkstyle" + " class-" + aid
    if all_codec_to_check is not None:
        if t not in all_codec_to_check:
            cls += (" " + "dehighlight-code-change")
    if all_invc_to_check is not None:
        if t in all_invc_to_check:
            cls += (" " + "highlight-inv-change")
    _, displayname, _, _, _, fullname = simplify_target_name(t, common_package=common_package)
    js_cmd = "return activateNeighbors_ws(" + "\"" + fullname + "\"" + ");"
    return "<a href='#' id='" + aid + "' class='" + cls + "' onclick='" + js_cmd + "'>" + displayname + "</a>"


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


def __append_script_hidden_packages(html_string):
    if config.extreme_simple_mode:
        extra_script = "    " + "extreme_simple_mode = true;\n"
    else:
        hidden_pkgs = config.hidden_package_names
        hidden_pkgs_str = ", ".join([("\"" + pkg + "\"") for pkg in hidden_pkgs])
        extra_script = "    " + "hidden_packages = [" + hidden_pkgs_str + "];\n"
    place_holder = "</script>\n</body>"
    to_replace = extra_script + place_holder
    return html_string.replace(place_holder, to_replace)


def __append_script_isotype_reset(html_string, iso):
    if iso:
        place_holder = "</script>\n</body>"
        reset_iso_script = "    " + "iso_type = \"si\";\n"
        to_replace = reset_iso_script + place_holder
        return html_string.replace(place_holder, to_replace)
    else:
        return html_string


def __purify_set_elements(aset):
    result = set()
    for ele in aset:
        result.add(purify_target_name(ele))
    return result


def __purify_map_map_elements(map_of_maps):
    result = {}
    for outer_key in map_of_maps:
        purified_outer_key = purify_target_name(outer_key)
        map_value = map_of_maps[outer_key]
        inner_map = {}
        for inner_key in map_value:
            purified_inner_key = purify_target_name(inner_key)
            inner_map[purified_inner_key] = map_value[inner_key]
        result[purified_outer_key] = inner_map
    return result


def _getty_csi_setvars(html_string, go, prev_hash, post_hash, common_package,
                       all_changed_tests, old_changed_tests, new_changed_tests,
                       all_changed_methods, new_all_src,
                       old_test_set, new_test_set,
                       old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                       new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                       all_whose_inv_changed, all_whose_clsobj_inv_changed, iso):
    all_changed_tests = __purify_set_elements(all_changed_tests)
    html_string = __append_script_l2s(html_string, all_changed_tests, "all_changed_tests")
    old_changed_tests = __purify_set_elements(old_changed_tests)
    html_string = __append_script_l2s(html_string, old_changed_tests, "old_changed_tests")
    new_changed_tests = __purify_set_elements(new_changed_tests)
    html_string = __append_script_l2s(html_string, new_changed_tests, "new_changed_tests")
    
    new_all = set()
    __set_all_with_tests(new_all, new_caller_of)
    __set_all_with_tests(new_all, new_callee_of)
    __set_all_with_tests(new_all, new_pred_of)
    __set_all_with_tests(new_all, new_succ_of)
    new_all = __purify_set_elements(new_all)
    html_string = __append_script_l2s(html_string, new_all, "all_project_methods")
    
    all_modified = set(all_changed_tests) | set(all_changed_methods)
    all_modified = __purify_set_elements(all_modified)
    html_string = __append_script_l2s(html_string, all_modified, "all_modified_targets")

#     new_all_test_and_else = new_all - set(new_all_src)
#     new_all_test_and_else = __purify_set_elements(new_all_test_and_else)
#     html_string = __append_script_l2s(html_string, new_all_test_and_else, "all_test_and_else")
    
    all_whose_inv_changed = __purify_set_elements(all_whose_inv_changed)
    html_string = __append_script_l2s(html_string, all_whose_inv_changed, "all_whose_inv_changed")
    all_whose_clsobj_inv_changed = __purify_set_elements(all_whose_clsobj_inv_changed)
    html_string = __append_script_l2s(html_string, all_whose_clsobj_inv_changed, "all_whose_clsobj_inv_changed")
    
#     # DEBUG ONLY
#     print new_caller_of
#     print new_callee_of
#     print new_pred_of
#     print new_succ_of
    
    old_caller_of = __purify_map_map_elements(old_caller_of)
    html_string = __append_script_mm2d(html_string, old_caller_of, "prev_affected_caller_of")
    old_callee_of = __purify_map_map_elements(old_callee_of)
    html_string = __append_script_mm2d(html_string, old_callee_of, "prev_affected_callee_of")
    old_pred_of = __purify_map_map_elements(old_pred_of)
    html_string = __append_script_mm2d(html_string, old_pred_of, "prev_affected_pred_of")
    old_succ_of = __purify_map_map_elements(old_succ_of)
    html_string = __append_script_mm2d(html_string, old_succ_of, "prev_affected_succ_of")
    new_caller_of = __purify_map_map_elements(new_caller_of)
    html_string = __append_script_mm2d(html_string, new_caller_of, "post_affected_caller_of")
    new_callee_of = __purify_map_map_elements(new_callee_of)
    html_string = __append_script_mm2d(html_string, new_callee_of, "post_affected_callee_of")
    new_pred_of = __purify_map_map_elements(new_pred_of)
    html_string = __append_script_mm2d(html_string, new_pred_of, "post_affected_pred_of")
    new_succ_of = __purify_map_map_elements(new_succ_of)
    html_string = __append_script_mm2d(html_string, new_succ_of, "post_affected_succ_of")
    
    html_string = __append_script_common_package(html_string, common_package)
    html_string = __append_script_hidden_packages(html_string)
    html_string = __append_script_isotype_reset(html_string, iso)
    
    return html_string
    

def getty_csi_targets_prep(html_file, go, prev_hash, post_hash, common_package,
                           all_changed_tests, old_changed_tests, new_changed_tests,
                           all_changed_methods, new_modified_src, new_all_src,
                           old_test_set, new_test_set,
                           old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                           new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                           old_refined_target_set, new_refined_target_set, refined_target_set,
                           all_classes_set, iso, expansion_set=None):    
    all_whose_inv_changed_candidates = set()
    if config.analyze_tests and not config.limit_interest:
        all_considered = (set(new_all_src) | set(new_test_set))
    elif config.limit_interest:
        all_considered = refined_target_set
    else:
        all_considered = set(new_all_src)
    if config.class_level_expansion:
        all_considered = all_considered | expansion_set
    
    for mtd in all_considered:
        if iso:
            if is_possibly_different(mtd, go, prev_hash, post_hash, preprocessed=True):
                all_whose_inv_changed_candidates.add(mtd);
        else:
            if is_different(mtd, go, prev_hash, post_hash):
                all_whose_inv_changed_candidates.add(mtd);
    
    all_whose_inv_changed = set()
    for one_target in all_whose_inv_changed_candidates:
        if one_target.find(":") != -1:
            all_whose_inv_changed.add(one_target) 
    
    all_whose_clsobj_inv_changed = set()
    for cls in all_classes_set:
        if iso:
            if is_possibly_different(cls, go, prev_hash, post_hash, preprocessed=True):
                all_whose_clsobj_inv_changed.add(cls)
        else:
            if is_different(cls, go, prev_hash, post_hash):
                all_whose_clsobj_inv_changed.add(cls)

    with open(html_file, 'r') as rf:
        html_string = rf.read()
    targets_place_holder = "<div id='csi-output-targets'></div>"
    cpkg_disclaimer = ""
    if common_package != '' and common_package is not None:
        common_package_display = "<span class='program-words'>" + common_package + "</span>"
        cpkg_disclaimer = "<div style='float:right;' class='target-top-row menu-words'>" + \
            "<b>Common Package:</b>&nbsp;&nbsp;" + common_package_display + "</div>"
    compare_commit_msgs = "<div class='target-top-row menu-words'><b>Compare Commits:</b>&nbsp;&nbsp;" + \
        "<a id='commit-msg-link' href='#'>" + prev_hash + " vs. " + post_hash + "</a></div>"
    replace_header = \
        "<div id='csi-output-targets'>" + cpkg_disclaimer + compare_commit_msgs + \
        "<div class='menu-words entry-header'><b>Updated Source:</b></div>"
    
    all_method_changes = set(all_changed_methods) | set(all_changed_tests)
    all_class_changes = set()
    for cm in all_method_changes:
        colon_pos = cm.find(":")
        if colon_pos != -1:
            all_class_changes.add(cm[:colon_pos])
        else:
            all_class_changes.add(cm)
    
    if all_changed_methods:
        replacement = "<div class='target-sep'>,</div>".join(
                            [__link_to_show_neighbors(t, common_package,
                                                      all_invc_to_check=all_whose_inv_changed)
                                for t in sorted(list(all_changed_methods))])
    else:
        replacement = "<span>None</span>"
    embed_test_update = "<br><div class='menu-words entry-header'><b>Updated Tests:</b></div>"
    if all_changed_tests:
        tests_replacement = "<div class='target-sep'>,</div>".join(
                                [__link_to_show_neighbors(t, common_package,
                                                          all_invc_to_check=all_whose_inv_changed)
                                    for t in sorted(list(all_changed_tests))])
    else:
        tests_replacement = "<span>None</span>"
    inv_change_update = \
        "<div class='menu-words entry-header'><b>Methods & Classes with Possible Invariant Changes </b></div>" + \
        create_show_hide_toggle("onoffswitch", "inv-change-list-sh",
            "$(\"div#invariant-change-list-divs\").toggle();return false;", checked=True,
            extra_style="margin-top:8px;")
    if all_whose_inv_changed or all_whose_clsobj_inv_changed:
        if all_whose_inv_changed:
            invch_mtd_replacement = "<span class='menu-words'>Methods: </span>" + \
                "<div class='target-sep'>,</div>".join(
                    [__link_to_show_neighbors(t, common_package,
                                              all_codec_to_check=all_method_changes)
                        for t in sorted(list(all_whose_inv_changed))])
        else:
            invch_mtd_replacement = "<span class='menu-words'>Methods: None</span>"
        if all_whose_clsobj_inv_changed:
            invch_cls_replacement = "<span class='menu-words'>Classes: </span>" + \
                "<div class='target-sep'>,</div>".join(
                    [__link_to_show_neighbors(t, common_package,
                                              all_codec_to_check=all_class_changes)
                        for t in sorted(list(all_whose_clsobj_inv_changed))])
        else:
            invch_cls_replacement = "<span class='menu-words'>Classes: None</span>"
        invch_replacement = invch_mtd_replacement + "<br>" + invch_cls_replacement
    else:
        invch_replacement = "<span>None</span>"
    invch_replacement = "<div id='invariant-change-list-divs'>" + invch_replacement + "</div>"
    replace_footer = "</div>"
    html_string = html_string.replace(targets_place_holder,
                                      replace_header + replacement + \
                                      embed_test_update + tests_replacement + \
                                      "<div>" + inv_change_update + invch_replacement + "</div>" + \
                                      replace_footer)

    html_string = _getty_csi_setvars(html_string, go, prev_hash, post_hash, common_package,
                                     all_changed_tests, old_changed_tests, new_changed_tests,
                                     all_changed_methods, new_all_src,
                                     old_test_set, new_test_set,
                                     old_caller_of, old_callee_of, old_pred_of, old_succ_of,
                                     new_caller_of, new_callee_of, new_pred_of, new_succ_of,
                                     all_whose_inv_changed, all_whose_clsobj_inv_changed, iso)
    
    with open(html_file, 'w') as wf:
        wf.write(html_string)
