#! /usr/bin/python
# coding=utf-8
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Transform a unified diff from stdin to a colored
# side-by-side HTML page on stdout.
#
# Authors: Olivier Matz <zer0@droids-corp.org>
#          Alan De Smet <adesmet@cs.wisc.edu>
#          Sergey Satskiy <sergey.satskiy@gmail.com>
#          scito <info at scito.ch>
#          Yan Yan <yayan@eng.ucsd.edu>
#
# Inspired by diff2html.rb from Dave Burt <dave (at) burt.id.au>
# (mainly for html theme)
#
# TODO:
# - The sane function currently mashes non-ASCII characters to "."
#   Instead be clever and convert to something like "xF0"
#   (the hex value), and mark with a <span>.  Even more clever:
#   Detect if the character is "printable" for whatever definition,
#   and display those directly.

import sys, re, htmlentitydefs, getopt, StringIO, codecs, datetime
try:
    from simplediff import diff, string_diff
except ImportError:
    raise EnvironmentError(
        "simplediff module is not installed - find it here: https://github.com/paulgb/simplediff\n")

from tools.daikon import fsformat
from tools.html import inv_to_html
from tools.os import from_sys_call_enforce


# minimum line size, we add a zero-sized breakable space every
# LINESIZE characters
linesize = 20
tabsize = 8
show_CR = False
encoding = "utf-8"
lang = "en"
algorithm = 0

desc = "File comparison"
dtnow = datetime.datetime.now()
modified_date = "%s+01:00"%dtnow.isoformat()

html_hdr = """<!DOCTYPE html>
<html lang="{5}" dir="ltr"
    xmlns:dc="http://purl.org/dc/terms/">
<head>
    <meta charset="{1}" />
    <meta name="generator" content="diff2html.py (http://git.droids-corp.org/gitweb/?p=diff2html)" />
    <!--meta name="author" content="Fill in" /-->
    <title>Semantiful Differentials{0}</title>
    <link rel="shortcut icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAgMAAABinRfyAAAACVBMVEXAAAAAgAD///+K/HwIAAAAJUlEQVQI12NYBQQM2IgGBQ4mCIEQW7oyK4phampkGIQAc1G1AQCRxCNbyW92oQAAAABJRU5ErkJggg==" type="image/png" />
    <meta property="dc:language" content="{5}" />
    <!--meta property="dc:date" content="{3}" /-->
    <meta property="dc:modified" content="{4}" />
    <meta name="description" content="{2}" />
    <meta property="dc:abstract" content="{2}" />
    <style>
        table {{ border:0px; border-collapse:collapse; width: 100%; font-size:0.75em; font-family: Lucida Console, monospace }}
        td.line {{ color:#8080a0 }}
        th {{ background: black; color: white }}
        tr.diffunmodified > td {{ background: #D0D0E0 }}
        tr.diffhunk > td {{ background: #A0A0A0 }}
        tr.diffadded > td {{ background: #CCFFCC }}
        tr.diffdeleted > td {{ background: #FFCCCC }}
        tr.diffchanged > td {{ background: #FFFFA0 }}
        span.diffchanged2 {{ background: #E0C880 }}
        span.diffponct {{ color: #B08080 }}
        tr.diffmisc td {{}}
        tr.diffseparator td {{}}
        tr.invheader > td {{ background: #A0A0A0; color: #C334A2; font-weight: bold }}
        .tooltip {{
            position: absolute;
            padding: 8px 15px;
            z-index: 2;
            color: #303030;
            background-color: #6FF1EB;
            border: 3px dashed #EC2D8E;
            font-family: sans-serif;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h3>GETTY - SEMANTIFUL DIFFERENTIALS</h3>
    <a href='#' id='getty-advice-title' onclick='return false;'>{{{{{{__getty_advice__}}}}}}</a><br>
    <a href='#' onclick='$(\"div#hide-all\").toggle();return false;'>show/hide more code and invariant diffs</a>
    <br><br>
    <div id='hide-all' style='display:block;'>
    {{{{{{__getty_code_diff__}}}}}}<br>
"""

html_footer = """
</div>
<footer>
    <p><br>--------<br>Modified at {1}. Getty - Semantiful Differentials.    </p>
</footer>
</body>
</html>
"""

table_hdr = """
        <table class="diff">
"""

table_footer = """
</table>
"""

DIFFON = "\x01"
DIFFOFF = "\x02"

buf = []
add_cpt, del_cpt = 0, 0
line1, line2 = 0, 0
hunk_off1, hunk_size1, hunk_off2, hunk_size2 = 0, 0, 0, 0


# Characters we're willing to word wrap on
WORDBREAK = " \t;.,/):-"


# for temp invariant files for prettier html diff
PRSV_LEFT = "[a/] -- "
PRSV_RIGHT = "[b/] -- "
PRSV_TMP = ".tagged.tmp"


def is_empty(table):
    return len(table) == 40


def sane(x):
    r = ""
    for i in x:
        j = ord(i)
        if i not in ['\t', '\n'] and (j < 32):
            r = r + "."
        else:
            r = r + i
    return r


def linediff(s, t):
    '''
    Original line diff algorithm of diff2html. It's character based.
    '''
    if len(s):
        s = unicode(reduce(lambda x, y:x+y, [ sane(c) for c in s ]))
    if len(t):
        t = unicode(reduce(lambda x, y:x+y, [ sane(c) for c in t ]))

    m, n = len(s), len(t)
    d = [[(0, 0) for i in range(n+1)] for i in range(m+1)]


    d[0][0] = (0, (0, 0))
    for i in range(m+1)[1:]:
        d[i][0] = (i,(i-1, 0))
    for j in range(n+1)[1:]:
        d[0][j] = (j,(0, j-1))

    for i in range(m+1)[1:]:
        for j in range(n+1)[1:]:
            if s[i-1] == t[j-1]:
                cost = 0
            else:
                cost = 1
            d[i][j] = min((d[i-1][j][0] + 1, (i-1, j)),
                          (d[i][j-1][0] + 1, (i, j-1)),
                          (d[i-1][j-1][0] + cost, (i-1, j-1)))

    l = []
    coord = (m, n)
    while coord != (0, 0):
        l.insert(0, coord)
        x, y = coord
        coord = d[x][y][1]

    l1 = []
    l2 = []

    for coord in l:
        cx, cy = coord
        child_val = d[cx][cy][0]

        father_coord = d[cx][cy][1]
        fx, fy = father_coord
        father_val = d[fx][fy][0]

        diff = (cx-fx, cy-fy)

        if diff == (0, 1):
            l1.append("")
            l2.append(DIFFON + t[fy] + DIFFOFF)
        elif diff == (1, 0):
            l1.append(DIFFON + s[fx] + DIFFOFF)
            l2.append("")
        elif child_val-father_val == 1:
            l1.append(DIFFON + s[fx] + DIFFOFF)
            l2.append(DIFFON + t[fy] + DIFFOFF)
        else:
            l1.append(s[fx])
            l2.append(t[fy])

    r1, r2 = (reduce(lambda x, y:x+y, l1), reduce(lambda x, y:x+y, l2))
    return r1, r2


def diff_changed(old, new):
    '''
    Returns the differences basend on characters between two strings
    wrapped with DIFFON and DIFFOFF using `diff`.
    '''
    con = {'=': (lambda x: x),
           '+': (lambda x: DIFFON + x + DIFFOFF),
           '-': (lambda x: '')}
    return "".join([(con[a])("".join(b)) for a, b in diff(old, new)])


def diff_changed_ts(old, new):
    '''
    Returns a tuple for a two sided comparison based on characters, see `diff_changed`.
    '''
    return (diff_changed(new, old), diff_changed(old, new))


def word_diff(old, new):
    '''
    Returns the difference between the old and new strings based on words. Punctuation is not part of the word.

    Params:
        old the old string
        new the new string

    Returns:
        the output of `diff` on the two strings after splitting them
        on whitespace (a list of change instructions; see the docstring
        of `diff`)
    '''
    separator_pattern = '(\W+)';
    return diff(re.split(separator_pattern, old, flags=re.UNICODE), re.split(separator_pattern, new, flags=re.UNICODE))


def diff_changed_words(old, new):
    '''
    Returns the difference between two strings based on words (see `word_diff`)
    wrapped with DIFFON and DIFFOFF.

    Returns:
        the output of the diff expressed delimited with DIFFON and DIFFOFF.
    '''
    con = {'=': (lambda x: x),
           '+': (lambda x: DIFFON + x + DIFFOFF),
           '-': (lambda x: '')}
    return "".join([(con[a])("".join(b)) for a, b in word_diff(old, new)])


def diff_changed_words_ts(old, new):
    '''
    Returns a tuple for a two sided comparison based on words, see `diff_changed_words`.
    '''
    return (diff_changed_words(new, old), diff_changed_words(old, new))


def convert(s, linesize=0, ponct=0):
    i = 0
    t = u""
    for c in s:
        # used by diffs
        if c == DIFFON:
            t += u'<span class="diffchanged2">'
        elif c == DIFFOFF:
            t += u"</span>"

        # special html chars
        elif htmlentitydefs.codepoint2name.has_key(ord(c)):
            t += u"&%s;" % (htmlentitydefs.codepoint2name[ord(c)])
            i += 1

        # special highlighted chars
        elif c == "\t" and ponct == 1:
            n = tabsize-(i%tabsize)
            if n == 0:
                n = tabsize
            t += (u'<span class="diffponct">&raquo;</span>'+'&nbsp;'*(n-1))
        elif c == " " and ponct == 1:
            t += u'<span class="diffponct">&middot;</span>'
        elif c == "\n" and ponct == 1:
            if show_CR:
                t += u'<span class="diffponct">\</span>'
        else:
            t += c
            i += 1

        if linesize and (WORDBREAK.count(c) == 1):
            t += u'&#8203;'
            i = 0
        if linesize and i > linesize:
            i = 0
            t += u"&#8203;"

    return t


def add_comment(s, output_file):
    if re.match("^diff --git", s):
        output_file.write(('<tr><td>&nbsp</td></tr>\n<tr class="diffmisc"><td colspan="4">%s</td></tr>\n'%convert(s)).encode(encoding))
    else:
        output_file.write(('<tr class="diffmisc"><td colspan="4">%s</td></tr>\n'%convert(s)).encode(encoding))


def __path_to_image(fpath):
    return "--" + re.sub("\W", "--", fpath) + "--"


preimage = ""
postimage = ""
prefile = ""
postfile = ""
image2filename = {}
oldl2m = {}
newl2m = {}
def __filepath_to_image(pathname):
    if pathname.startswith("/"):
        return "_dev_null_"
    elif pathname.startswith("a/") or pathname.startswith("b/"):
        filepath = re.match("^(a|b)/(.*)", pathname).group(2)
        imagename = __path_to_image(filepath)
        image2filename[imagename] = filepath 
        return imagename
    elif pathname == "BEFORE" or pathname == "AFTER":
        return ""
    else:
        return None


def add_filename(f1, f2, output_file):
    global preimage
    global postimage
    global prefile
    global postfile
    global image2filename
    preimage = __filepath_to_image(f1)
    postimage = __filepath_to_image(f2)
    prefile = (f1[2:] if not f1.startswith("/") else f1)
    postfile = (f2[2:] if not f2.startswith("/") else f2)
    output_file.write(("<tr><th colspan='2'>%s</th>"%convert(f1, linesize=linesize)).encode(encoding))
    output_file.write(("<th colspan='2'>%s</th></tr>\n"%convert(f2, linesize=linesize)).encode(encoding))


def add_hunk(output_file, show_hunk_infos):
    if show_hunk_infos:
        output_file.write('<tr class="diffhunk"><td colspan="2">Offset %d, %d lines modified</td>'%(hunk_off1, hunk_size1))
        output_file.write('<td colspan="2">Offset %d, %d lines modified</td></tr>\n'%(hunk_off2, hunk_size2))
    else:
        # &#8942; - vertical ellipsis
        output_file.write('<tr class="diffhunk"><td colspan="2">&#8942;</td><td colspan="2">&#8942;</td></tr>')


def add_line(s1, s2, output_file):
    global line1
    global line2
    
    global oldl2m
    global newl2m

    orig1 = s1
    orig2 = s2
    
    line1_active_flag = False
    line2_active_flag = False

    if s1 == None and s2 == None:
        type_name = "unmodified"
    elif s1 == None or s1 == "":
        type_name = "added " + postimage
        line2_active_flag = True
    elif s2 == None or s1 == "":
        type_name = "deleted " + preimage
        line1_active_flag = True
    elif s1 == s2:
        type_name = "unmodified"
    else:
        type_name = "changed " + postimage
        line2_active_flag = True
        if algorithm == 1:
            s1, s2 = diff_changed_words_ts(orig1, orig2)
        elif algorithm == 2:
            s1, s2 = diff_changed_ts(orig1, orig2)
        else: # default
            s1, s2 = linediff(orig1, orig2)
    
    if (not line1_active_flag) and (not line2_active_flag):
        pass
    elif line2_active_flag:
        possible_nk = (postfile, int(line2))
        if possible_nk in newl2m:
            type_name += (" -related-" + fsformat(newl2m[possible_nk]))
    elif line1_active_flag:
        possible_ok = (prefile, int(line1))
        if possible_ok in oldl2m:
            type_name += (" -related-" + fsformat(oldl2m[possible_ok]))
    else:
        raise ValueError("adding a line with wrong flags: " + str(line1_active_flag) + " " + str(line2_active_flag))
    
    if (orig1 is not None and orig1.startswith(PRSV_LEFT)) or \
            (orig2 is not None and orig2.startswith(PRSV_RIGHT)):
        output_file.write(('<tr class="invheader diff%s">' % type_name).encode(encoding))
    else:
        if ((orig1 is None or str(orig1).strip() == "") and 
            (orig2 is not None and str(orig2).strip().startswith("================"))) or \
             ((orig2 is None or str(orig2).strip() == "") and 
              (orig1 is not None and str(orig1).strip().startswith("================"))) or \
             (orig1 is None and orig2 is not None and str(orig2).strip() == "") or \
             (orig2 is None and orig1 is not None and str(orig1).strip() == ""):
            output_file.write(('<tr class="diff-ignore diff%s">' % type_name).encode(encoding))
        else:
            output_file.write(('<tr class="diff%s">' % type_name).encode(encoding))
    
    if s1 != None and s1 != "":
        output_file.write(('<td class="diffline">%d </td>' % line1).encode(encoding))
        output_file.write('<td class="diffpresent">'.encode(encoding))
        output_file.write(convert(s1, linesize=linesize, ponct=1).encode(encoding))
        output_file.write('</td>')
    else:
        s1 = ""
        output_file.write('<td colspan="2"> </td>')

    if s2 != None and s2 != "":
        output_file.write(('<td class="diffline">%d </td>'%line2).encode(encoding))
        output_file.write('<td class="diffpresent">')
        output_file.write(convert(s2, linesize=linesize, ponct=1).encode(encoding))
        output_file.write('</td>')
    else:
        s2 = ""
        output_file.write('<td colspan="2"></td>')

    output_file.write('</tr>\n')

    if s1 != "":
        line1 += 1
    if s2 != "":
        line2 += 1


def empty_buffer(output_file):
    global buf
    global add_cpt
    global del_cpt

    if del_cpt == 0 or add_cpt == 0:
        for l in buf:
            add_line(l[0], l[1], output_file)

    elif del_cpt != 0 and add_cpt != 0:
        l0, l1 = [], []
        for l in buf:
            if l[0] != None:
                l0.append(l[0])
            if l[1] != None:
                l1.append(l[1])
        max_len = (len(l0) > len(l1)) and len(l0) or len(l1)
        for i in range(max_len):
            s0, s1 = "", ""
            if i < len(l0):
                s0 = l0[i]
            if i < len(l1):
                s1 = l1[i]
            add_line(s0, s1, output_file)

    add_cpt, del_cpt = 0, 0
    buf = []


def parse_input(input_file, output_file, input_file_name, output_file_name,
                exclude_headers, show_hunk_infos):
    global add_cpt, del_cpt
    global line1, line2
    global hunk_off1, hunk_size1, hunk_off2, hunk_size2

    if not exclude_headers:
        title_suffix = ' ' + input_file_name
        output_file.write(html_hdr.format(title_suffix, encoding, desc, "", modified_date, lang).encode(encoding))
    output_file.write(table_hdr.encode(encoding))

    while True:
        l = input_file.readline()
        if l == "":
            break
        
        m = re.match('^--- ([^\s]*)', l)
        if m:
            empty_buffer(output_file)
            file1 = m.groups()[0]
            while True:
                l = input_file.readline()
                m = re.match('^\+\+\+ ([^\s]*)', l)
                if m:
                    file2 = m.groups()[0]
                    break
            add_filename(file1, file2, output_file)
            hunk_off1, hunk_size1, hunk_off2, hunk_size2 = 0, 0, 0, 0
            continue

        m = re.match("@@ -(\d+),?(\d*) \+(\d+),?(\d*)", l)
        if m:
            empty_buffer(output_file)
            hunk_data = map(lambda x:x=="" and 1 or int(x), m.groups())
            hunk_off1, hunk_size1, hunk_off2, hunk_size2 = hunk_data
            line1, line2 = hunk_off1, hunk_off2
            add_hunk(output_file, show_hunk_infos)
            continue

        if hunk_size1 == 0 and hunk_size2 == 0:
            empty_buffer(output_file)
            add_comment(l, output_file)
            continue

        if re.match("^\+", l):
            add_cpt += 1
            hunk_size2 -= 1
            buf.append((None, l[1:]))
            continue

        if re.match("^\-", l):
            del_cpt += 1
            hunk_size1 -= 1
            buf.append((l[1:], None))
            continue

        if re.match("^\ ", l) and hunk_size1 and hunk_size2:
            empty_buffer(output_file)
            hunk_size1 -= 1
            hunk_size2 -= 1
            buf.append((l[1:], l[1:]))
            continue
        
        empty_buffer(output_file)
        add_comment(l, output_file)

    empty_buffer(output_file)
    output_file.write(table_footer.encode(encoding))
    if not exclude_headers:
        output_file.write("<br>{{{__getty_invariant_diff__}}}<br>")
        output_file.write("<br>{{{__getty_invariants__}}}<br>")
        output_file.write("<br>{{{__getty_source_code__}}}<br>")
        output_file.write(html_footer.format("", dtnow.strftime("%b. %d, %Y")).encode(encoding))


def usage():
    print '''
diff2html.py [-e encoding] [-i file] [-o file] [-x]
diff2html.py -h

Transform a unified diff from stdin to a colored side-by-side HTML
page on stdout.
stdout may not work with UTF-8, instead use -o option.

   -i file     set input file, else use stdin
   -e encoding set file encoding (default utf-8)
   -o file     set output file, else use stdout
   -x          exclude html header and footer
   -t tabsize  set tab size (default 8)
   -l linesize set maximum line size is there is no word break (default 20)
   -r          show \\r characters
   -k          show hunk infos
   -a algo     line diff algorithm (0: linediff characters, 1: word, 2: simplediff characters) (default 0)
   -h          show help and exit
'''


def main():
    global linesize, tabsize
    global show_CR
    global encoding
    global algorithm

    input_file_name = ''
    output_file_name = ''

    exclude_headers = False
    show_hunk_infos = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "he:i:o:xt:l:rka:",
                                   ["help", "encoding=", "input=", "output=",
                                    "exclude-html-headers", "tabsize=",
                                    "linesize=", "show-cr", "show-hunk-infos", "algorithm="])
    except getopt.GetoptError, err:
        print unicode(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    verbose = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-e", "--encoding"):
            encoding = a
        elif o in ("-i", "--input"):
            input_file = codecs.open(a, "r", encoding)
            input_file_name = a
        elif o in ("-o", "--output"):
            output_file = codecs.open(a, "w")
            output_file_name = a
        elif o in ("-x", "--exclude-html-headers"):
            exclude_headers = True
        elif o in ("-t", "--tabsize"):
            tabsize = int(a)
        elif o in ("-l", "--linesize"):
            linesize = int(a)
        elif o in ("-r", "--show-cr"):
            show_CR = True
        elif o in ("-k", "--show-hunk-infos"):
            show_hunk_infos = True
        elif o in ("-a", "--algorithm"):
            algorithm = int(a)
        else:
            assert False, "unhandled option"

    # Use stdin if not input file is set
    if not ('input_file' in locals()):
        input_file = codecs.getreader(encoding)(sys.stdin)

    # Use stdout if not output file is set
    if not ('output_file' in locals()):
        output_file = codecs.getwriter(encoding)(sys.stdout)

    parse_input(input_file, output_file, input_file_name, output_file_name,
                exclude_headers, show_hunk_infos)


def parse_from_memory(txt, exclude_headers, show_hunk_infos):
    " Parses diff from memory and returns a string with html "
    input_stream = StringIO.StringIO(txt)
    output_stream = StringIO.StringIO()
    parse_input(input_stream, output_stream, '', '', exclude_headers, show_hunk_infos)
    return output_stream.getvalue()


def diff_to_html(input_diff_file, output_html_file, exclude_headers=False, old_l2m={}, new_l2m={}):
    global oldl2m
    global newl2m
    oldl2m = old_l2m
    newl2m = new_l2m
    with open(input_diff_file, 'r') as input, open(output_html_file, 'w') as output:
        parse_input(input, output, '', '', exclude_headers, True)


def __denoise(dstring):
    """taken off noise of 'git diff' for invariant diffs
    """
    lines = dstring.split("\n")
    rawlines = []
    for line in lines:
        if line.startswith("diff --git"):
            rawlines.append("diff --invariants a/BEFORE b/AFTER")
        elif re.match("^---\ .*", line):
            rawlines.append("--- BEFORE")
        elif re.match("^\+\+\+\ .*", line):
            rawlines.append("+++ AFTER")
        elif re.match("^(\+|-|\ |@@ ).*", line):
            rawlines.append(line)
        else:
            pass
    return "\n".join(rawlines)


def __escape(target):
    return target.replace("<", "&lt;").replace(">", "&gt;")


def __prediff_process(file_name, preserve_tag, postfix):
    content = ""
    try:
        with open(file_name, 'r') as rf:
            content = rf.read()
    except IOError:
        non_exist = '<DOES NOT EXIST>'
        with open(file_name, 'w') as wf:
            wf.write(non_exist)
        content = non_exist
    new_content = []
    for line in content.split("\n"):
        if re.match(".*:::(ENTER|EXIT|CLASS|OBJECT|THROW).*", line):
            line = preserve_tag + line
        new_content.append(line)
    new_file_name = file_name + PRSV_TMP
    with open(new_file_name, 'w') as wf:
        wf.write("\n".join(new_content))
    return new_file_name


def _getty_append_invdiff(html_string, targets, go, prev_hash, curr_hash):
    for target in sorted(targets, reverse=True):
        tfs = fsformat(target)
        
        prev_invs_file = go + "_getty_inv__" + tfs + "__" + prev_hash + "_.inv.txt"
        prev_invs_file_tagged = __prediff_process(prev_invs_file, PRSV_LEFT, PRSV_TMP)
        curr_invs_file = go + "_getty_inv__" + tfs + "__" + curr_hash + "_.inv.txt"
        curr_invs_file_tagged = __prediff_process(curr_invs_file, PRSV_RIGHT, PRSV_TMP)
        dstring = from_sys_call_enforce(
            " ".join(["git diff --unified=0", prev_invs_file_tagged, curr_invs_file_tagged]))
        
        dstring = __denoise(dstring)
        dtable = parse_from_memory(dstring, True, False)
        anchor = "<br>{{{__getty_invariant_diff__}}}<br>"
        inv_title = "<br>compare inviants for { <b>" + __escape(target) + "</b> }<br>"
        invdiffhtml = \
            "<div id='vsinvs-" + fsformat(target) + "' style='min-width:960px'>" + \
            inv_title + "\n" + dtable + \
            ("NO DIFFERENCE" if is_empty(dtable) else "") + \
            "\n</div>\n"
        invdiff_out = go + "_getty_inv__" + tfs + "__" + ".inv.diff.html"
        with open(invdiff_out, 'w') as idout:
            idout.write(invdiffhtml)
        replacement = anchor + "\n" + invdiffhtml
        html_string = html_string.replace(anchor, replacement)
    from_sys_call_enforce("rm " + go + "*" + PRSV_TMP)
    return html_string


def _import_js(html_string, js_path):
    import_script = "<script type=\"text/javascript\" src=\"{0}\"></script>"
    import_jquery = import_script.format(js_path + "jquery-1.2.6.js")
    import_simpletip = import_script.format(js_path + "jquery.simpletip-1.3.1.js")
    import_buckets = import_script.format(js_path + "buckets.min.js")
    import_getty = import_script.format(js_path + "getty.js")
    last_import = "\n".join([import_jquery, import_simpletip, import_buckets, import_getty, "</body>"])
    return html_string.replace("</body>", last_import)


def __add_inv_js_line(html_string, tfs, prev_hash, prev_invs, curr_hash, curr_invs):
    prev_script_line = "    $('invariants#" + tfs + "').data('" + prev_hash + "', '" + \
        prev_invs.replace("'", "\\'").replace("\n", "\\n") + "');\n"
    curr_script_line = "    $('invariants#" + tfs + "').data('" + curr_hash + "', '" + \
        curr_invs.replace("'", "\\'").replace("\n", "\\n") + "');\n"
    replacement = prev_script_line + curr_script_line + "</script>\n</body>"
    html_string = html_string.replace("</script>\n</body>", replacement)
    return html_string


def _getty_append_invariants(html_string, targets, go, prev_hash, curr_hash):
    html_string = html_string.replace("</body>", "<script>\n</script>\n</body>")
    for target in sorted(targets):
        tfs = fsformat(target)
        prev_invs_file = go + "_getty_inv__" + tfs + "__" + prev_hash + "_.inv.txt"
        with open(prev_invs_file, 'r') as prevf:
            prev_invs = prevf.read()
        curr_invs_file = go + "_getty_inv__" + tfs + "__" + curr_hash + "_.inv.txt"
        with open(curr_invs_file, 'r') as currf:
            curr_invs = currf.read()
        # html replacement
        anchor_html = "<br>{{{__getty_invariants__}}}<br>"
        invs_html = "<invariants id='" + tfs + "'></invariants>"
        rpmt_html = anchor_html + "\n" + invs_html + "\n"
        html_string = html_string.replace(anchor_html, rpmt_html)
        # javascript replacement
        html_string = __add_inv_js_line(html_string, tfs, prev_hash, prev_invs, curr_hash, curr_invs)
    return html_string


def _getty_install_invtips(html_string, prev_hash, curr_hash, go, oldl2m, newl2m):
    newarray = ["\"" + curr_hash + "\""]
    for pair in newl2m:
        newarray.append("\"" + __path_to_image(pair[0]) + "\"")
        newarray.append("\"" + str(pair[1]) + "\"")
        newarray.append("\"" + fsformat(newl2m[pair]) + "\"")
    newarray_str = "[" + ", ".join(t for t in newarray) + "]"
    
    oldarray = ["\"" + prev_hash + "\""]
    for pair in oldl2m:
        oldarray.append("\"" + __path_to_image(pair[0]) + "\"")
        oldarray.append("\"" + str(pair[1]) + "\"")
        oldarray.append("\"" + fsformat(oldl2m[pair]) + "\"")
    oldarray_str = "[" + ", ".join(t for t in oldarray) + "]"
    
    install_line = \
        "<script>\n" + \
        "    installInvTips(" + \
        "\"" + curr_hash + "\", " + "\"" + prev_hash + "\", " + \
        newarray_str + ", " + oldarray_str + ");\n" + \
        "    $(\"div#hide-all\").toggle();\n" + \
        "    $(\"tr.diffhunk\").hide();\n" + \
        "    $(\"tr.diff-ignore\").hide();\n" + \
        "</script>\n</body>"
    html_string = html_string.replace("</body>", install_line)
    return html_string


def getty_append_semainfo(template_file, targets, go, js_path, prev_hash, curr_hash, old_l2m, new_l2m):
    global oldl2m
    global newl2m
    oldl2m = old_l2m
    newl2m = new_l2m
    
    if not go.endswith("/"):
        go = go + "/"
    
    html_string = ""
    with open(template_file, 'r') as rf:
        html_string = rf.read()
    
    html_string = _getty_append_invdiff(html_string, targets, go, prev_hash, curr_hash)
    html_string = _import_js(html_string, js_path)
#     html_string = _getty_append_invariants(html_string, targets, go, prev_hash, curr_hash)
    inv_to_html(targets, go, prev_hash)
    inv_to_html(targets, go, curr_hash)
    html_string = _getty_install_invtips(html_string, prev_hash, curr_hash, go, old_l2m, new_l2m)
    
    with open(template_file, 'w') as wf:
        wf.write(html_string)


if __name__ == "__main__":
    main()
