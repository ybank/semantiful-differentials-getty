# html transformation and manipulation

import config
from tools.daikon import fsformat
from tools.ex import read_str_from


inv_html_header = """<!-- inv html header -->
<head>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <link rel="stylesheet" type="text/css" href="styles_inv.css?ver={0}">
</head>
<pre class="prettyprint linenums"><code>
""".format(config.version_time)

inv_html_footer = """
</code></pre><script src="./run_prettify.js"></script>
"""

legends = "<div id='legends'><div style='float:right;'><br>" + \
    "<span class='program-words'>" + \
    "<span><u>method_name</u>: source code was changed</span><br>" + \
    "<span>" + \
    "  <span style='color:red;'>method_name</span>: invariants were changed" + \
    "</span><br>" + \
    "<span>" + \
    "  <span style='color:darkgray;'>method_name</span>: invariants were NOT changed" + \
    "</span><br>" + \
    "<span>method_name <b>(x + y)</b>: <br>" + \
    "&nbsp;&nbsp;before the commit, this method is called x times;<br>" + \
    "&nbsp;&nbsp;after the commit, it is called y more times<br></span>" + \
    "<br><span>Example: <span style='color:darkgray'><u>foobar</u> (5 - 2)</span></span><br>" + \
    "&nbsp;&nbsp;foobar\'s code has been changed, but invariants were not.<br>" + \
    "&nbsp;&nbsp;It was executed 5 times before, and now 2 times less, 3.<br><br>" + \
    "</span></div></div>"

def inv_to_html(targets, go, commit_hash):
#     filtered_targets = [t for t in targets if not t.endswith(":<clinit>")]
    for target in targets:
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
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <link rel="stylesheet" type="text/css" href="{0}styles_src.css?ver={1}">
</head>
<pre class="prettyprint linenums"><code>"""

src_html_footer = """
</code></pre><script src="../{0}run_prettify.js"></script>
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
                    allsrc + src_html_footer.format("../" * lvs)
            with open(jp + ".html", 'w') as wf:
                wf.write(newsrchtml)
        except:
            pass

def create_show_hide_toggle(btn_name, btn_id, cb_fn_str, checked=True, extra_style=None):
    cm = " checked" if checked else ""
    es = "" if extra_style is None else " style='" + extra_style + "'"
    return "<div class='onoffswitch'" + es + ">" + \
        "<input type='checkbox' name='" + btn_name + "' class='onoffswitch-checkbox' " + \
        "id='" + btn_id + "' onchange='" + cb_fn_str + "'" + cm + ">" + \
        "<label class='onoffswitch-label' for='" + btn_id + "'>" + \
        "<span class='onoffswitch-inner'></span><span class='onoffswitch-switch'></span>" + \
        "</label></div>"

def create_legends_tooltip():
    return "<div style='float:right;'><a id='legends-tooltip' href='#'>Legends</a></div>"
