# give advices and present them to users

from analysis.rubrics import warning_ccc
from tools.daikon import fsformat


def examine_cccs(cccs):
    warnings = []
    for method_key in cccs:
        for ccc in cccs[method_key]:
            if warning_ccc(ccc):
                warnings.append(ccc)
    return warnings


advice_file = "advice.html"
report_header = """<!-- advise report header -->
<head>
    <style>
        .ccc { display: block; }
        span { display: inline-block; }
        span.arrow-no-wrap { white-space: pre; }
        table { border:0px; border-collapse:collapse; width: 100%; font-size:0.75em; font-family: Lucida Console, monospace }
        td.line { color:#8080a0 }
        th { background: black; color: white }
        tr.diffunmodified > td { background: #D0D0E0 }
        tr.diffhunk > td { background: #A0A0A0 }
        tr.diffadded > td { background: #CCFFCC }
        tr.diffdeleted > td { background: #FFCCCC }
        tr.diffchanged > td { background: #FFFFA0 }
        span.diffchanged2 { background: #E0C880 }
        span.diffponct { color: #B08080 }
        tr.diffmisc td {}
        tr.diffseparator td {}
        .tooltip {
            position: absolute;
            padding: 8px 15px;
            z-index: 2;
            color: #303030;
            background-color: #BEBEE8;
            border: 3px dotted #EC2D8E;
            font-family: sans-serif;
            font-size: 14px;
        }
    </style>
</head>
<body>
"""
report_foorter = """<!-- advise report footer -->
<br>{{{__getty_invariant_diff__}}}<br>
</body>
"""

def _method_span(m):
    if m.startswith("@"):
        return "<span class='report-" + fsformat(m[1:]) + "'>recur: " + m[1:] + "</span>"
    elif m.startswith("!"):
        return "<span>" + "..." + "</span>"
    else:
        return "<span class='report-" + fsformat(m) + "'>" + m + "</span>"


def _with_invdiff(report_html, targets, go):
    anchor = "<br>{{{__getty_invariant_diff__}}}<br>"
    for target in sorted(targets, reverse=True):
        invdiff_file = go + "_getty_inv__" + fsformat(target) + "__" + ".inv.diff.html"
        with open(invdiff_file, 'r') as invdiff:
            invdiff_html = invdiff.read()
        replacement = anchor + "\n" + invdiff_html + "\n"
        report_html = report_html.replace(anchor, replacement)
    return report_html


def _with_tips(page, targets, prev_hash, post_hash, go, jspath):
    import_script = "<script type=\"text/javascript\" src=\"{0}\"></script>\n"
    import_jquery = import_script.format(jspath + "jquery-3.1.1.min.js")
    import_simpletip = import_script.format(jspath + "jquery.simpletip-1.3.2.js")
    import_getty = import_script.format(jspath + "getty.js")
    targets_str = "[" + ", ".join("\"" + fsformat(t) + "\"" for t in targets) + "]"
    hashes_str = "\"" + prev_hash + "\", \"" + post_hash + "\""
    install_tips = \
        "<script>\n" + \
        "    installInvTips4Advice(" + targets_str + ", " + hashes_str + ");\n" + \
        "</script>\n"
    last_import = import_jquery + import_simpletip + import_getty + install_tips + "</body>"
    return page.replace("</body>", last_import)


def report(targets, cccs, prev_hash, post_hash, go, fe_path):
    warnings = examine_cccs(cccs)
    with open(go + advice_file, "w") as report_file:
        report_html = report_header
        report_html += "    <span>further inspect the following possible method invocations:</span><br><br>\n"
        if not warnings:
            report_html += "<div><span>none</span></div>\n"
        for warning in warnings:
            hw = [_method_span(w) for w in warning]
            visualized_ccc = "<span class='arrow-no-wrap'>&nbsp;&nbsp;--->&nbsp;&nbsp;</span>".join(reversed(hw))
            report_html += ("    <div class='ccc'>" + visualized_ccc + "</div><br>\n")
        report_html += report_foorter
        report_html = _with_invdiff(report_html, targets, go)
        report_html = _with_tips(report_html, targets, prev_hash, post_hash, go, fe_path)
        report_file.write(report_html)


def getty_append_report(template_file):
    with open(template_file, "r") as rf:
        html_string = rf.read()
    install_advice = \
        "<script>\n" + \
        "    installAdvisorTips(\"" + advice_file + "\");\n" + \
        "</script>\n</body>"
    html_string = html_string.replace("</body>", install_advice)
    with open(template_file, "w") as wf:
        wf.write(html_string)
