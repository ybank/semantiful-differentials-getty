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
        invs = invs.replace("<", "&lt;").replace(">", "&gt;")
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


src_html_header = """<!-- getty src html header -->
<style>
    pre.prettyprint { display: block; background-color: #333 }
    pre .nocode { background-color: none; color: #000 }
    pre .str { color: #ffa0a0 }
    pre .kwd { color: #f0e68c; font-weight: bold }
    pre .com { color: #87ceeb }
    pre .typ { color: #98fb98 }
    pre .lit { color: #cd5c5c }
    pre .pun { color: #fff }
    pre .pln { color: #fff }
    pre .tag { color: #f0e68c; font-weight: bold }
    pre .atn { color: #bdb76b; font-weight: bold }
    pre .atv { color: #ffa0a0 }
    pre .dec { color: #98fb98 }

    ol.linenums { margin-top: 0; margin-bottom: 0; color: #AEAEAE }
    li.L0,li.L1,li.L2,li.L3,li.L5,li.L6,li.L7,li.L8,li.L9 {
      list-style-type: decimal !important;
      background: #333 !important;
    }

    @media print {
      pre.prettyprint { background-color: none }
      pre .str, code .str { color: #060 }
      pre .kwd, code .kwd { color: #006; font-weight: bold }
      pre .com, code .com { color: #600; font-style: italic }
      pre .typ, code .typ { color: #404; font-weight: bold }
      pre .lit, code .lit { color: #044 }
      pre .pun, code .pun { color: #440 }
      pre .pln, code .pln { color: #000 }
      pre .tag, code .tag { color: #006; font-weight: bold }
      pre .atn, code .atn { color: #404 }
      pre .atv, code .atv { color: #060 }
    }
</style>
<pre class="prettyprint linenums"><code>"""

src_html_footer = """<!-- src html footer -->
</code></pre><script src="../=LEVELS=run_prettify.js"></script>
"""

def _target_to_path(method_name):
    colon_index = method_name.rfind(":")
    dollar_index = method_name.find("$")
    if colon_index != -1:
        if dollar_index == -1:
            rel_path = method_name[:colon_index].replace(".", "/")
        else:
            rel_path = method_name[:dollar_index].replace(".", "/")
    else:
        if dollar_index == -1:
            rel_path = method_name[:].replace(".", "/")
        else:
            rel_path = method_name[:dollar_index].replace(".", "/")
    return rel_path + ".java", rel_path.count("/")


def _to_real_footer(levels):
    levelstr = ""
    for i in range(levels):
        levelstr += "../"
    return src_html_footer.replace("=LEVELS=", levelstr)


def src_to_html(targets, go, commit_hash):
    filehash = {}
    for target in targets:
        tp, lv = _target_to_path(target)
        if tp not in filehash:
            filehash[go + "_getty_allcode_" + commit_hash + "_/" + tp] = lv
    for jp in filehash:
        try:
            print "syntax highlighting: " + jp
            with open(jp, "r+") as f:
                allsrc = f.read()
                newsrchtml = src_html_header + allsrc + _to_real_footer(filehash[jp])
                f.seek(0)
                f.truncate()
                f.write(newsrchtml)
        except:
            pass
