# html transformation and manipulation

from tools.daikon import fsformat


inv_html_header = """<!-- inv html header -->
<head>
    <style>
        pre {
            background-color: #5A5F5A;
            color: white;
            word-wrap: break-word;
        }
    </style>
</head>
<body><pre>
"""

inv_html_footer = """<!-- inv html footer -->
</pre></body>
"""

def inv_to_html(targets, go, commit_hash):
    for target in targets:
        tfs = fsformat(target)
        invs_file = go + "_getty_inv__" + tfs + "__" + commit_hash + "_.inv.txt"
        with open(invs_file, 'r') as invf:
            invs = invf.read()
        invs_html = go + "_getty_inv__" + tfs + "__" + commit_hash + "_.inv.html"
        with open(invs_html, 'w') as invh:
            content = inv_html_header
            lines = invs.split("\n")
            ln_span = len(str(len(lines)))
            line_number = 1
            for line in lines:
                ln_str = str(line_number)
                len_ln_str = len(ln_str)
                if len_ln_str < ln_span:
                    ln_str = (ln_span - len_ln_str) * "&nbsp;" + ln_str
                ln_str += "|&nbsp;"
                content += ("<a name='" + str(line_number) + "' /><span>" + ln_str + "</span>" + line + "\n")
                line_number += 1
            content += inv_html_footer
            invh.write(content)
