# html transformation and manipulation

from tools.daikon import fsformat


inv_html_header = """<!-- inv html header -->
<style>
    pre .str { color: #EC7600; }
    pre .kwd { color: #93C763; }
    pre .com { color: #66747B; }
    pre .typ { color: #AAC9E8; }
    pre .lit { color: #FACD22; }
    pre .pun { color: #F1F2F3; }
    pre .pln { color: #F1F2F3; }
    pre .tag { color: #8AC763; }
    pre .atn { color: #E0E2E4; }
    pre .atv { color: #EC7600; }
    pre .dec { color: purple; }
    pre.prettyprint {
        border: none !important;
        background: #000;
        font-family:'Droid Sans Mono','CPMono_v07','Droid Sans';
        font-size: 9pt;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    body { margin: 0 !important; }
    ol.linenums {
        margin-top: 0;
        margin-bottom: 0;
        padding-left: 24px;
    }
    li.L0, li.L1, li.L2, li.L3, li.L4, li.L5, li.L6, li.L7, li.L8, li.L9 {
        color: #555;
        list-style-type: decimal !important;
    }
    li.L1, li.L3, li.L5, li.L7, li.L9 {
        background: #111 !important;
    }
</style>
<pre class="prettyprint linenums"><code>
"""

inv_html_footer = """
</code></pre><script src="./run_prettify.js"></script>
"""

def inv_to_html(targets, go, commit_hash):
    filtered_targets = [t for t in targets if not t.endswith(":<clinit>")]
    for target in filtered_targets:
        tfs = fsformat(target)
        invs_file = go + "_getty_inv__" + tfs + "__" + commit_hash + "_.inv.out"
        try:
            with open(invs_file, 'r+') as invf:
                invs = invf.read()
                newinvhtml = inv_html_header + invs + inv_html_footer
                invf.seek(0)
                invf.truncate()
                invf.write(newinvhtml)
        except IOError:
            with open(invs_file, 'w') as newf:
                newf.write("<NO INVARIANTS INFERRED>")


src_html_header = """<!-- src html header -->
<style>
    pre.prettyprint {
        display: block;
        background-color: #333;
        border: none !important;
        font-size: 9pt;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
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
    body { margin: 0 !important; }
    ol.linenums { margin-top: 0; margin-bottom: 0; color: #AEAEAE }
    li.L0,li.L1,li.L2,li.L3,li.L5,li.L6,li.L7,li.L8,li.L9 {
      list-style-type: decimal !important;
      background: #333 !important;
    }
</style>
<pre class="prettyprint linenums"><code>"""

src_html_footer = """
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
    for _ in range(levels):
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
            with open(jp, "r+") as javaf:
                allsrc = javaf.read()
                newsrchtml = src_html_header + allsrc + _to_real_footer(filehash[jp])
                javaf.seek(0)
                javaf.truncate()
                javaf.write(newsrchtml)
        except:
            pass
