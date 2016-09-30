# html transformation and manipulation

import config
from tools.daikon import fsformat
from tools.ex import read_str_from


inv_html_header = """<!-- inv html header -->
<head>
  <link rel="stylesheet" type="text/css" href="styles_inv.css?ver={0}">
</head>
<pre class="prettyprint linenums"><code>
""".format(config.version_time)

inv_html_footer = """
</code></pre><script src="./run_prettify.js"></script>
"""

def inv_to_html(targets, go, commit_hash):
    filtered_targets = [t for t in targets if not t.endswith(":<clinit>")]
    for target in filtered_targets:
        tfs = fsformat(target)
        invs_file = go + "_getty_inv__" + tfs + "__" + commit_hash + "_.inv.out"
        try:
            with open(invs_file, 'r') as invf:
                invs = invf.read()
                newinvhtml = inv_html_header + invs + inv_html_footer
            with open(invs_file + ".html", "w") as wf:
                wf.write(newinvhtml)
        except IOError:
            with open(invs_file + ".html", 'w') as newf:
                newf.write("<NO INVARIANTS INFERRED>")


src_html_header = """<!-- src html header -->
<head>
  <link rel="stylesheet" type="text/css" href="{0}styles_src.css?ver={1}">
</head>
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
    levelstr += ("../" * levels)
    return src_html_footer.replace("=LEVELS=", levelstr)


def _install_anchors_for(original, targets, l4ms):
    l2as = {}
    for target in targets:
        if target in l4ms:
            l2as[l4ms[target]] = "<a name='" + fsformat(target) + "'></a>"
    if len(l2as) > 0:
        installed = []
        for line_number, line_content in enumerate(original.split("\n"), start=1):
            if line_number in l2as:
                installed.append(l2as[line_number] + line_content)
            else:
                installed.append(line_content)
        return '\n'.join(installed)
    else:
        return original


def src_to_html(targets, go, commit_hash, install_line_numbers=False):
    filehash = {}
    if install_line_numbers:
        f2ts = {}
        l4ms = read_str_from(go + "_getty_alll4m_" + commit_hash + "_.ex")
    for target in targets:
        tp, lv = _target_to_path(target)
        real_path = go + "_getty_allcode_" + commit_hash + "_/" + tp
        if real_path not in filehash:
            filehash[real_path] = lv
        if install_line_numbers:
            if real_path not in f2ts:
                f2ts[real_path] = set()
            f2ts[real_path].add(target)
    for jp in filehash:
        try:
            print "preprocessing: " + jp
            with open(jp, "r") as javaf:
                allsrc = javaf.read()
                if install_line_numbers:
                    print "  -- installing anchors ..."
                    allsrc = _install_anchors_for(allsrc, f2ts[jp], l4ms)
                print "  -- syntax highlighting ..."
                lvs = filehash[jp]
                newsrchtml = \
                    src_html_header.format(
                        "../" * (lvs + 1), config.version_time) + \
                    allsrc + _to_real_footer(lvs)
            with open(jp + ".html", 'w') as wf:
                wf.write(newsrchtml)
        except:
            pass
