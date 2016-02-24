# give advices and present them to users

from analysis.rubrics import warning_ccc


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
        .ccc {
            display: block;
        }
    </style>
</head>
<body>
"""
report_foorter = """<!-- advise report footer -->
</body>
"""

def report(cccs, go):
    warnings = examine_cccs(cccs)
    with open(go + advice_file, "w") as report_file:
        report_html = report_header
        report_html += "<span>further inspect the following possible method invocations:</span><br><br>\n"
        if not warnings:
            report_html += "<div><span>none</span></div>"
        for warning in warnings:
            visualized_ccc = " ---> ".join(warning)
            report_html += ("    <div class='ccc'>" + visualized_ccc + "</div>")
        report_html += report_foorter
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
    
