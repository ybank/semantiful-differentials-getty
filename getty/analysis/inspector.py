# CSI inspection page section


from analysis.solver import is_different
from tools.daikon import fsformat


def getty_csi_init(html_file):
    html_string = ""
    with open(html_file, 'r') as rf:
        html_string = rf.read()
    html_string = html_string.replace(
        "<a href='#' id='getty-advice-title' onclick='return false;'>{{{__getty_advice__}}}</a>",
        "{{{__getty_continuous_semantic_inspection__}}}" + \
        "<div id='csi-output-targets'></div>\n" + \
        "<div id='csi-output-neighbors' " + \
        "style='border:4px double gray; padding: 4px 4px 4px 4px; margin: 8px 0 0 0;'>" + \
        "Choose a target to show its affected neighbors</div>\n" + \
        "<div id='csi-output-invcomp' " + \
        "style='border:4px double gray; padding: 4px 4px 4px 4px; margin: 8px 0 0 0;'>" + \
        "Choose a neighbor target to show its invariant change</div>")
    with open(html_file, 'w') as wf:
        wf.write(html_string)


def getty_csi_targets_prep(html_file, go, prev_hash, post_hash):
    html_string = ""
    with open(html_file, 'r') as rf:
        html_string = rf.read()
    targets_place_holder = "<div id='csi-output-targets'></div>"
    replace_header = \
        "<div id='csi-output-targets' " + \
        "style='border:4px ridge gray; padding: 4px 4px 4px 4px; margin: 8px 0 0 0;'>" + \
        "<h4 style='margin: 4px 0 8px 0'>Updated Method Targets:</h4>"
    replace_footer = "</div>"
    replacement = "the targets will be here"
    html_string = html_string.replace(targets_place_holder, replace_header + replacement + replace_footer)
    with open(html_file, 'w') as wf:
        wf.write(html_string)
