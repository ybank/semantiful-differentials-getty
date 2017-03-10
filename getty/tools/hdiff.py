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

import sys, re, htmlentitydefs, getopt, StringIO, codecs, datetime, difflib, json

import config
# from analysis import solver
from tools.daikon import fsformat_with_sigs
from tools.html import inv_to_html, create_show_hide_toggle, legends
from tools.os import from_sys_call_enforce, remove_many_files
from tools.diffutil import diff


# minimum line size, we add a zero-sized breakable space every
# LINESIZE characters
linesize = 20
tabsize = 8
show_CR = False
encoding = "utf-8"
lang = "en"
algorithm = 1

desc = "File comparison"
dtnow = datetime.datetime.now()
modified_date = "%s+01:00"%dtnow.isoformat()

basic_html_hdr = """<!DOCTYPE html>
<html lang="{5}" dir="ltr"
    xmlns:dc="http://purl.org/dc/terms/">
<head>
    <meta charset="{1}" />
    <title>Getty - Semantiful Differentials {0}</title>
    <link rel="shortcut icon"
        href="data:image/png;base64,
            iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAgMAAABinRfyAAAACVBMVEXAAAAAgAD///
            +K/HwIAAAAJUlEQVQI12NYBQQM2IgGBQ4mCIEQW7oyK4phampkGIQAc1G1AQCRxCNbyW92oQAAAABJRU5ErkJggg=="
        type="image/png" />
    <link rel="stylesheet" type="text/css" href="styles.css?ver={6}">
    <link rel="stylesheet" type="text/css" href="jquery-ui-1.12.1.min.css?ver={6}">
    <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
    <meta property="dc:language" content="{5}" />
    <!--meta property="dc:date" content="{3}" /-->
    <meta property="dc:modified" content="{4}" />
    <meta name="description" content="{2}" />
    <meta property="dc:abstract" content="{2}" />
</head>
"""

html_hdr = basic_html_hdr + """
<body style='overflow-y:scroll;'>
    __getty_stub__
    <div style='padding-left:4px;' id='sh-srcdiff-switch'>
      <div class='menu-words' style='margin: 24px 0 8px 0;'>
        List of All Code Changes&nbsp;&nbsp;
        {0}
    </div></div>
    <div id='getty-full-code-diff' style="display:none;">
""".format(create_show_hide_toggle('btn-sh-sd', 'btn-sh-sd',
                '$(\"div#getty-full-code-diff\").toggle();return false;', checked=False))

continue_hdr = """</div>
    <div style='display:none;padding-left:4px;margin-top:8px;' id='sh-invdiff-switch'>
      <div class='menu-words' style='margin: 24px 0 8px 0;'>
        List of Invariant Differentials&nbsp;&nbsp;
        {0}
    </div></div>
    <div id='getty-full-inv-diff' style='display:none;'>
""".format(create_show_hide_toggle('btn-sh-id', 'btn-sh-id',
                '$(\"div#getty-full-inv-diff\").toggle();return false;', checked=False))

footer_info = """<footer>
    <p><br>--------<br>Generated at {0}. Getty - Semantiful Differentials.    </p>
</footer>
"""

html_footer = """
</div>
{0}
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
WORDBREAK = " \t;.,/)]}:-"

# When the line is too long to be analyzed and shown
TOO_LONG_MSG = "THIS LINE IS TOO LONG TO BE SHOWN: "

# for temp invariant files for prettier html diff
PRSV_LEFT = "[a/] -- "
PRSV_RIGHT = "[b/] -- "
PRSV_LEN = max(len(PRSV_LEFT), len(PRSV_RIGHT))
PRSV_TMP = ".tagged.tmp"

# anchor prefix for finding the first line of target change
TARGET_ANCHOR_PREFIX = "-getty-ta-"

# for matching invariant point headers
header_regex = "^(.*\[.*(a|b).*/.*\].*-.*-).*:.*:.*:.*"
orig_header_regex = "^(\[(a|b)/\] -- ).*:::(ENTER|EXIT|CLASS|OBJECT|THROW).*"


# TODO: ideally, the table should be parsed to decide whether it is empty
def is_empty(table):
    return (
        table.count("<table class=\"diff\">") == 1 and
        table.count("<tr") <= 2 and
        table.count("<tr class=\"diffmisc\">") <= 1 and
        table.count("<tr>") <= 1
    ) or (
        table.count("<table class=\"diff\">") == 2 and
        table.count("<tr") <= 3 and
        table.count("<tr class=\"diffmisc\">") <= 2 and
        table.count("<tr>") <= 1
    )


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
    d = [[(0, 0) for _ in range(n+1)] for _ in range(m+1)]


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
    diff_result = diff(old, new)
    return "".join([(con[a])("".join(b)) for a, b in diff_result])


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
    subject_a = re.split(separator_pattern, old, flags=re.UNICODE)
    subject_b = re.split(separator_pattern, new, flags=re.UNICODE)
    diff_result = diff(subject_a, subject_b)
    return diff_result


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
            try:
                t += c
            except UnicodeDecodeError:
                t += u"?"
            i += 1

        if linesize and (WORDBREAK.count(c) == 1):
            t += u'&#8203;'
            i = 0
        if linesize and i > linesize:
            i = 0
            t += u"&#8203;"

    return t


def add_comment(s, output_file, with_ln=True):
    thenarrow = str(2 if with_ln else 1)
    thewide = str(48 if with_ln else 49)
    ph_ln_td = "<td colspan='1' style='width:" + thenarrow + "%'>&nbsp;</td>"
    ph_ln_td_e = "<td colspan='1' style='width:" + thenarrow + "%'></td>"
    ph_content_td = "<td colspan='1' style='width:" + thewide + "%'></td>"
    fixed_layout_first_row = ph_ln_td + ph_content_td + ph_ln_td + ph_content_td
    fixed_layout_empty_row = ph_ln_td_e + ph_content_td + ph_ln_td_e + ph_content_td
    if re.match("^diff --git", s):
        output_file.write(
            ('<tr class="diffmisc">' + fixed_layout_first_row + '</tr>\n' +
             '<tr><td colspan=\'4\'>%s</td></tr>\n'%convert(s)).encode(encoding))
    else:
        output_file.write(
            ('<tr class="diffmisc">' + fixed_layout_empty_row + '</tr>\n').encode(encoding))


def __path_to_image(fpath):
    return "--" + re.sub("\W", "--", fpath) + "--"


prefile = None
postfile = None
oldl2m = {}
newl2m = {}


def __hunkpath_to_filepath(hp):
    if hp.startswith("/"):
        return None
    elif hp.startswith("a/") or hp.startswith("b/"):
        return hp[2:]
    else:
        return None


def add_filename(f1, f2, output_file, same_table=True):
    global prefile
    global postfile
    prefile = __hunkpath_to_filepath(f1)
    postfile = __hunkpath_to_filepath(f2)
    display1 = f1 if f1 != "BEFORE" else "REMOVED"
    output_file.write(("<tr><th colspan='2'>%s</th>"%convert(display1, linesize=linesize)).encode(encoding))
    display2 = f2 if f2 != "AFTER" else "ADDED"
    output_file.write(("<th colspan='2'>%s</th></tr>\n"%convert(display2, linesize=linesize)).encode(encoding))
    if not same_table:
        output_file.write("</table>\n<div class='scrollable-table'>" + table_hdr)
        add_comment("empty-row", output_file, with_ln=False)


def add_hunk(output_file, show_hunk_infos):
    if show_hunk_infos:
        output_file.write('<tr class="diffhunk"><td colspan="2">Offset %d, %d lines modified</td>'%(hunk_off1, hunk_size1))
        output_file.write('<td colspan="2">Offset %d, %d lines modified</td></tr>\n'%(hunk_off2, hunk_size2))
    else:
        if show_hunk_infos is not None:
            # &#8942; - vertical ellipsis
            output_file.write('<tr class="diffhunk"><td colspan="2">&#8942;</td><td colspan="2">&#8942;</td></tr>')


def _ln(ln, show):
    if show:
        return str(ln)
    else:
        return ""


cached_header = None
caching_stage = False
ignore_all_ws = False
def add_line(s1, s2, output_file, with_ln=True):
    global line1
    global line2
    
    global oldl2m
    global newl2m
    
    global cached_header
    global caching_stage
    global ignore_all_ws

    orig1 = s1
    orig2 = s2
    
    line1_active_flag = False
    line2_active_flag = False

    if s1 is None and s2 is None:
        type_name = "unmodified"
    if (s1 is None or (len(s1) <= 1 and s1.strip() == "")) and \
            (s2 is None or (len(s2) <= 1 and s2.strip() == "")):
        if ignore_all_ws:
            type_name = "-ignore"
        else:
            type_name = "unmodified"
    elif (s1 is None or s1.strip() == "") and s2 is not None:
        type_name = "added"
        line2_active_flag = True
    elif (s2 is None or s2.strip() == "") and s1 is not None:
        type_name = "deleted"
        line1_active_flag = True
    elif s1 == s2 and not (s1.startswith(TOO_LONG_MSG) and s2.startswith(TOO_LONG_MSG)):
        type_name = "unmodified"
    else:
        type_name = "changed"
        line2_active_flag = True
        if algorithm == 1:
            s1, s2 = diff_changed_words_ts(orig1, orig2)
        elif algorithm == 2:
            s1, s2 = diff_changed_ts(orig1, orig2)
        else: # default
            s1, s2 = linediff(orig1, orig2)
    
    extra_anchor_names = set()
    
    if (not line1_active_flag) and (not line2_active_flag):
        extra_anchor_names.clear()
    else:
        if line2_active_flag:
            possible_nk = (postfile, int(line2))
            if possible_nk in newl2m:
                extra_anchor_names.add(TARGET_ANCHOR_PREFIX + fsformat_with_sigs(newl2m[possible_nk]))
        if line1_active_flag:
            possible_ok = (prefile, int(line1))
            if possible_ok in oldl2m:
                extra_anchor_names.add(TARGET_ANCHOR_PREFIX + fsformat_with_sigs(oldl2m[possible_ok]))
    
    if (orig1 is not None and orig1.startswith(PRSV_LEFT)) or \
            (orig2 is not None and orig2.startswith(PRSV_RIGHT)):
        cached_header = ('<tr class="invheader diff%s">' % type_name).encode(encoding)
        caching_stage = True
    else:
        if ((orig1 is None or str(orig1).strip() == "") and 
            (orig2 is not None and str(orig2).strip().startswith("================"))) or \
             ((orig2 is None or str(orig2).strip() == "") and 
              (orig1 is not None and str(orig1).strip().startswith("================"))) or \
             ((orig1 is not None and str(orig1).strip().startswith("================")) and
              (orig2 is not None and str(orig2).strip().startswith("================"))) or \
             (orig1 is None and orig2 is not None and str(orig2).strip() == "") or \
             (orig2 is None and orig1 is not None and str(orig1).strip() == "") or \
             (orig1 is not None and orig2 is not None and type_name == "unmodified" and not with_ln) or \
             (ignore_all_ws and str(orig1).strip() == "" and str(orig2).strip() == ""):
            if caching_stage:
                cached_header += (('<tr class="diff-ignore diff%s">' % type_name).encode(encoding))
            else:
                output_file.write(('<tr class="diff-ignore diff%s">' % type_name).encode(encoding))
        else:
            if cached_header is not None:
                output_file.write(cached_header)
                cached_header = None
            if caching_stage:
                caching_stage = False
            output_file.write(('<tr class="diff%s">' % type_name).encode(encoding))

    if caching_stage:
        om1 = re.match(orig_header_regex, str(orig1))
        if om1:
            m1 = re.match(header_regex, str(s1))
            s1 = str(s1)[len(m1.group(1)):].strip() if m1 else str(s1).strip()
        om2 = re.match(orig_header_regex, str(orig2))
        if om2:
            m2 = re.match(header_regex, str(s2))
            s2 = str(s2)[len(m2.group(1)):].strip() if m2 else str(s2).strip()

        if s1 != None and s1 != "":
            cached_header += (('<td class="diffline">%s </td>' % _ln(line1, with_ln)).encode(encoding))
            cached_header += ('<td class="diffpresent">'.encode(encoding))
            cached_header += (convert(s1, linesize=linesize, ponct=1).encode(encoding))
            cached_header += ('</td>')
        else:
            s1 = ""
            cached_header += ('<td colspan="2"></td>')

        if s2 != None and s2 != "":
            if with_ln:
                cached_header += (
                    ('<td class="diffline">%s </td>' % _ln(line2, with_ln)).encode(encoding))
            else:
                cached_header += (
                    ('<td class="diffline with_liner">%s </td>' % _ln(line2, with_ln)).encode(encoding))
            cached_header += ('<td class="diffpresent">')
            cached_header += (convert(s2, linesize=linesize, ponct=1).encode(encoding))
            cached_header += ('</td>')
        else:
            s2 = ""
            if with_ln:
                cached_header += ('<td colspan="2"></td>')
            else:
                cached_header += ('<td class="with_liner" colspan="2"></td>')
        cached_header += ('</tr>\n')
    else:
        extra_anchors = ""
        for ean in extra_anchor_names:
            extra_anchors += ("<a name='" + ean + "'></a>")
        if s1 != None and s1 != "":
            output_file.write(
                ('<td class="diffline">' +
                 extra_anchors +
                 '%s </td>' % _ln(line1, with_ln)).encode(encoding))
            output_file.write('<td class="diffpresent">'.encode(encoding))
            output_file.write(convert(s1, linesize=linesize, ponct=1).encode(encoding))
            output_file.write('</td>')
        else:
            s1 = ""
            output_file.write('<td colspan="2">' + extra_anchors + '</td>')
    
        if s2 != None and s2 != "":
            if with_ln:
                output_file.write(
                    ('<td class="diffline">%s </td>' % _ln(line2, with_ln)).encode(encoding))
            else:
                output_file.write(
                    ('<td class="diffline with_liner">%s </td>' % _ln(line2, with_ln)).encode(encoding))
            output_file.write('<td class="diffpresent">')
            output_file.write(convert(s2, linesize=linesize, ponct=1).encode(encoding))
            output_file.write('</td>')
        else:
            s2 = ""
            if with_ln:
                output_file.write('<td colspan="2"></td>')
            else:
                output_file.write('<td class="with_liner" colspan="2"></td>')
        output_file.write('</tr>\n')
    
    if s1 != "":
        line1 += 1
    if s2 != "":
        line2 += 1


inv_header_general_regex = ".*\(.*\):::(ENTER|EXIT(\d*)|THROW(S)?(COMBINED)?).*"
def _calc_similarity(a, b, ma=None, mb=None):
    if ma is None:
        ma = re.match(inv_header_general_regex, a)
    if mb is None:
        mb = re.match(inv_header_general_regex, b)
    if ma and mb:
        if ma.group(1) != mb.group(1):
            return 0
        elif ((ma.group(2) != mb.group(2) or
               ma.group(3) != mb.group(3) or
               ma.group(4) != mb.group(4)) and
              ((ma.group(2) is None and mb.group(2) is not None) or
               (ma.group(2) is not None and mb.group(2) is None) or
               (ma.group(3) is None and mb.group(3) is not None) or
               (ma.group(3) is not None and mb.group(3) is None) or
               (ma.group(4) is None and mb.group(4) is not None) or
               (ma.group(4) is not None and mb.group(4) is None))):
            return 0
    elif ma or mb:
        return 0
    if ma and mb:
        raw_a = a[PRSV_LEN:]
        raw_b = b[PRSV_LEN:]
        return difflib.SequenceMatcher(a=raw_a, b=raw_b).ratio()
    else:
        return difflib.SequenceMatcher(a=a, b=b).ratio()


def empty_buffer(output_file, with_ln=True):
    global buf
    global add_cpt
    global del_cpt

    if del_cpt == 0 or add_cpt == 0:
        for l in buf:
            add_line(l[0], l[1], output_file, with_ln=with_ln)

    elif del_cpt != 0 and add_cpt != 0:
        l0, l1 = [], []
        for l in buf:
            if l[0] != None:
                l0.append(l[0])
            if l[1] != None:
                l1.append(l[1])
        
        l0size = len(l0)
        l1size = len(l1)
        if config.change_alignment:
            difflines = []
            left_index = 0
            right_index = 0
            threshold = config.similarity_bar
            while left_index < l0size and right_index < l1size:
                fm_index = None
                ma = re.match(inv_header_general_regex, l0[left_index])
                for i in range(right_index, l1size):
                    similarity = _calc_similarity(l0[left_index], l1[i], ma=ma)
                    if similarity >= threshold:
                        fm_index = i
                        break
                if fm_index is None:
                    difflines.append((l0[left_index], None))
                    left_index += 1
                    if ma:
                        while (left_index < l0size and
                               not re.match(inv_header_general_regex, l0[left_index])):
                            difflines.append((l0[left_index], None))
                            left_index += 1
                else:
                    for j in range(right_index, fm_index):
                        difflines.append((None, l1[j]))
                    difflines.append((l0[left_index], l1[fm_index]))
                    right_index = fm_index + 1
                    left_index += 1
            if left_index < l0size:
                for k in range(left_index, l0size):
                    difflines.append((l0[k], None))
            if right_index < l1size:
                for l in range(right_index, l1size):
                    difflines.append((None, l1[l]))
            for aline in difflines:
                add_line(aline[0], aline[1], output_file, with_ln=with_ln)
        else:
            max_len = max(l0size, l1size)
            for i in range(max_len):
                s0, s1 = "", ""
                if i < l0size:
                    s0 = l0[i]
                if i < l1size:
                    s1 = l1[i]
                add_line(s0, s1, output_file, with_ln=with_ln)

    add_cpt, del_cpt = 0, 0
    buf = []


def parse_input(input_file, output_file, input_file_name, output_file_name,
                exclude_headers, show_hunk_infos, with_ln=True, cont=False):
    global add_cpt, del_cpt
    global line1, line2
    global hunk_off1, hunk_size1, hunk_off2, hunk_size2

    title_suffix = ' ' + input_file_name
    if not exclude_headers:
        if exclude_headers is None:
            output_file.write(basic_html_hdr.format(
                    title_suffix, encoding, desc, "",
                    modified_date, lang, config.version_time).encode(encoding))
        else:
            output_file.write(html_hdr.format(
                    title_suffix, encoding, desc, "",
                    modified_date, lang, config.version_time).encode(encoding))
    
    output_file.write(table_hdr.encode(encoding))

    while True:
        l = input_file.readline()
        if l == "":
            break
        
        m = re.match('^--- ([^\s]*)', l)
        if m:
            empty_buffer(output_file, with_ln=with_ln)
            file1 = m.groups()[0]
            while True:
                l = input_file.readline()
                m = re.match('^\+\+\+ ([^\s]*)', l)
                if m:
                    file2 = m.groups()[0]
                    break
            add_filename(file1, file2, output_file, same_table=with_ln)
            hunk_off1, hunk_size1, hunk_off2, hunk_size2 = 0, 0, 0, 0
            continue

        m = re.match("@@ -(\d+),?(\d*) \+(\d+),?(\d*)", l)
        if m:
            empty_buffer(output_file, with_ln=with_ln)
            hunk_data = map(lambda x:x=="" and 1 or int(x), m.groups())
            hunk_off1, hunk_size1, hunk_off2, hunk_size2 = hunk_data
            line1, line2 = hunk_off1, hunk_off2
            add_hunk(output_file, show_hunk_infos)
            continue

        if hunk_size1 == 0 and hunk_size2 == 0:
            empty_buffer(output_file, with_ln=with_ln)
            add_comment(l, output_file, with_ln=with_ln)
            continue

        if re.match("^\+", l):
            add_cpt += 1
            hunk_size2 -= 1
            if len(l) - 1 <= config.max_diff_line_size:
                buf.append((None, l[1:]))
            else:
                too_long_msg = TOO_LONG_MSG + l[1:20]
                buf.append((None, too_long_msg))
            continue

        if re.match("^\-", l):
            del_cpt += 1
            hunk_size1 -= 1
            if len(l) - 1 <= config.max_diff_line_size:
                buf.append((l[1:], None))
            else:
                too_long_msg = TOO_LONG_MSG + l[1:20]
                buf.append((too_long_msg, None))
            continue

        if re.match("^\ ", l) and hunk_size1 and hunk_size2:
            empty_buffer(output_file, with_ln=with_ln)
            hunk_size1 -= 1
            hunk_size2 -= 1
            buf.append((l[1:], l[1:]))
            continue
        
        empty_buffer(output_file, with_ln=with_ln)
        add_comment(l, output_file, with_ln=with_ln)

    empty_buffer(output_file, with_ln=with_ln)
    output_file.write(table_footer.encode(encoding))
    if not with_ln:
        output_file.write("\n</div>")
    
    if cont:
        output_file.write(continue_hdr)
    
    if not exclude_headers:
        if exclude_headers is not None:
            output_file.write("<br>{{{__getty_invariant_diff__}}}<br>")
            output_file.write(
                html_footer.format(
                    footer_info.format(dtnow.strftime("%b. %d, %Y"))).encode(encoding))
        else:
            output_file.write(html_footer.format("").encode(encoding))


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
   -a algo     line diff algorithm (0: linediff characters, 1: word, 2: simplediff characters) (default 1)
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


def parse_from_memory(txt, exclude_headers, show_hunk_infos, with_ln=True):
    " Parses diff from memory and returns a string with html "
    input_stream = StringIO.StringIO(txt)
    output_stream = StringIO.StringIO()
    parse_input(input_stream, output_stream, '', '', exclude_headers, show_hunk_infos, with_ln=with_ln)
    return output_stream.getvalue()


def srcdiff2html(input_diff_file, output_html_file,
                 exclude_headers=None, old_l2m={}, new_l2m={}):
    global oldl2m
    global newl2m
    oldl2m = old_l2m
    newl2m = new_l2m
    with open(input_diff_file, 'r') as inputf, open(output_html_file, 'w') as outputf:
        parse_input(inputf, outputf, '', '', exclude_headers, None, with_ln=True, cont=False)


def diff_to_html(input_diff_file, output_html_file,
                 exclude_headers=False, old_l2m={}, new_l2m={}):
    global oldl2m
    global newl2m
    oldl2m = old_l2m
    newl2m = new_l2m
    with open(input_diff_file, 'r') as inputf, open(output_html_file, 'w') as outputf:
        parse_input(inputf, outputf, '', '', exclude_headers, None, cont=True)


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
    result = target.replace("<", "&lt;").replace(">", "&gt;")
    last_dash_pos = result.rfind("-")
    if last_dash_pos == -1:
        return result
    else:
        return result[:last_dash_pos]


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


def __prediff_process_in_memory(file_name, preserve_tag):
    try:
        with open(file_name, 'r') as rf:
            content = rf.read()
            new_content = []
            for line in content.split("\n"):
                if re.match(".*:::(ENTER|EXIT|CLASS|OBJECT|THROW).*", line):
                    line = preserve_tag + line
                new_content.append(line + "\n")
            return new_content
    except IOError:
        return ['<DOES NOT EXIST>']


def __generate_append_diff(target, diff_type, prev_invf, post_invf, diff_htmlf):
    global cached_header
    global caching_stage
    if diff_type not in ["ni", "ti4o", "ti4n", "si"]:
        raise ValueError("diff_type must be one of 'ni', 'ti4o', 'ti4n', and 'si'")
    if config.use_tmp_files:
        prev_invs_file_tagged = __prediff_process(prev_invf, PRSV_LEFT, PRSV_TMP)
        curr_invs_file_tagged = __prediff_process(post_invf, PRSV_RIGHT, PRSV_TMP)
        dstring = from_sys_call_enforce(
            " ".join(["git diff", "--unified="+str(config.inv_diff_context_lines),
                      prev_invs_file_tagged, curr_invs_file_tagged]))
    else:
        prev_invs_tagged = __prediff_process_in_memory(prev_invf, PRSV_LEFT)
        curr_invs_tagged = __prediff_process_in_memory(post_invf, PRSV_RIGHT)
        dstring = "diff --git a/invariants b/invariants\n"
        for ln in difflib.unified_diff(prev_invs_tagged, curr_invs_tagged,
                                       n=config.inv_diff_context_lines):
            dstring += ln

    cached_header = None
    caching_stage = False
    if len(dstring.split("\n")) <= config.max_diff_lines:
        dstring = __denoise(dstring)
        dtable = parse_from_memory(dstring, True, None, with_ln=False)
    else:
        print '   --- too big diff to be shown'
        dtable = '<div>The differential is too big to be shown</div>'
    
    inv_title = \
        "<div class='inv-cmp-title'><span class='menu-words'>Compare Invariants for</span> " + \
        "{ <span class='program-words'><b>" + __escape(target) + "</b></span> }</div>"
    invdiffhtml = \
        "<div id='vsinvs-" + diff_type + "-" + fsformat_with_sigs(target) + "'>" + \
        inv_title + "\n" + \
        ("NO DIFFERENCE" if is_empty(dtable) else dtable) + \
        "\n</div>\n"
    with open(diff_htmlf, 'w') as idout:
        idout.write(invdiffhtml)
    return invdiffhtml


def _getty_append_invdiff(html_string, targets, go, prev_hash, curr_hash, iso):
    global ignore_all_ws
    ignore_all_ws = True
    anchor = "<br>{{{__getty_invariant_diff__}}}<br>"
    for target in sorted(targets, reverse=True):
        if config.install_diffinv_only:
            print '  -- processing inv diff for ' + target
            tfs = fsformat_with_sigs(target)
            osot_invf = go + "_getty_inv__" + tfs + "__" + prev_hash + "_.inv.out"
            nsnt_invf = go + "_getty_inv__" + tfs + "__" + curr_hash + "_.inv.out"
            invdiff_outft = go + "_getty_inv__" + tfs + "__" + ".inv.diff.html"
            diff_settings = [("ni", osot_invf, nsnt_invf, invdiff_outft)]
            if iso:
                osnt_invf = go + "_getty_inv__" + tfs + "__" + prev_hash + "_" + curr_hash + "_.inv.out"
                nsot_invf = go + "_getty_inv__" + tfs + "__" + curr_hash + "_" + prev_hash + "_.inv.out"
                diff_settings += [
                    ("si", osnt_invf, nsnt_invf, invdiff_outft[:-10]+".si.diff.html"),
                    ("ti4o", osot_invf, osnt_invf, invdiff_outft[:-10]+".ti4o.diff.html"),
                    ("ti4n", nsot_invf, nsnt_invf, invdiff_outft[:-10]+".ti4n.diff.html")]
            for ds in diff_settings:
                replacement = anchor + "\n" + \
                    __generate_append_diff(target, ds[0], ds[1], ds[2], ds[3])
                html_string = html_string.replace(anchor, replacement)
    html_string = html_string.replace(anchor, "")
    if config.use_tmp_files:
        remove_many_files(go, "*"+PRSV_TMP)
    ignore_all_ws = False
    return html_string


def _import_js(html_string, fe_path, go):
    import_script = "<script type=\"text/javascript\" src=\"{0}\"></script>"
    last_import = []
    for cssfile in ["styles.css", "styles_inv.css", "styles_src.css", "jquery-ui-1.12.1.min.css"]:
        from_sys_call_enforce(" ".join(["cp", fe_path + cssfile, go + cssfile]))
    for jslib in ["jquery-3.1.1.min.js", "jquery-ui-1.12.1.min.js", "jquery.simpletip-1.3.2.js",
                  "buckets.min.js", "run_prettify.js", "getty.js"]:
        from_sys_call_enforce(" ".join(["cp", fe_path + jslib, go + jslib]))
        last_import.append(import_script.format(jslib + "?ver=" + config.version_time))
    last_import.append("</body>")
    last_import_str = "\n".join(last_import)
    return html_string.replace("</body>", last_import_str)


def __add_inv_js_line(html_string, tfs, prev_hash, prev_invs, curr_hash, curr_invs):
    prev_script_line = "    $('invariants#" + tfs + "').data('" + prev_hash + "', '" + \
        prev_invs.replace("'", "\\'").replace("\n", "\\n") + "');\n"
    curr_script_line = "    $('invariants#" + tfs + "').data('" + curr_hash + "', '" + \
        curr_invs.replace("'", "\\'").replace("\n", "\\n") + "');\n"
    replacement = prev_script_line + curr_script_line + "</script>\n</body>"
    html_string = html_string.replace("</script>\n</body>", replacement)
    return html_string


def _getty_install_invtips(html_string, commit_msgs, github_link,
                           prev_hash, curr_hash, go, oldl2m, newl2m, iso):
    extra_tooltips_installation = "    set_commit_hashes(" + \
        "\"" + prev_hash + "\", " + "\"" + curr_hash + "\");\n"
    if config.install_extra_tips:
        newarray = ["\"" + curr_hash + "\""]
        if config.install_inv_tips:
            for pair in newl2m:
                newarray.append("\"" + __path_to_image(pair[0]) + "\"")
                newarray.append("\"" + str(pair[1]) + "\"")
                newarray.append("\"" + fsformat_with_sigs(newl2m[pair]) + "\"")
        newarray_str = "[" + ", ".join(t for t in newarray) + "]"
        
        oldarray = ["\"" + prev_hash + "\""]
        if config.install_inv_tips:
            for pair in oldl2m:
                oldarray.append("\"" + __path_to_image(pair[0]) + "\"")
                oldarray.append("\"" + str(pair[1]) + "\"")
                oldarray.append("\"" + fsformat_with_sigs(oldl2m[pair]) + "\"")
        oldarray_str = "[" + ", ".join(t for t in oldarray) + "]"
        
        extra_tooltips_installation = \
            "    installInvTips(" + \
            "\"" + curr_hash + "\", " + "\"" + prev_hash + "\", " + \
            newarray_str + ", " + oldarray_str + ");\n"
    
    iso_setup = ""
    if iso:
        iso_setup = "    isolation = true;\n"
    
    js_commit_msgs = json.dumps(commit_msgs)
    js_github_link = (json.dumps(github_link) if github_link is not None else "''")
    
    install_line = \
        "<script>\n" + \
        "    install_msg_tips(" + js_commit_msgs + ", " + js_github_link + ");\n" + \
        "    install_legend_tips(\"" + legends + "\");\n" + \
        "    window.onbeforeunload = function() { return true; };\n" + \
        iso_setup + extra_tooltips_installation + \
        "    $(\"tr.diff-ignore\").hide();\n" + \
        "</script>\n</body>"
    html_string = html_string.replace("</body>", install_line)
    return html_string


def getty_append_semainfo(template_file, targets, go, fe_path,
                          commit_msgs, github_link,
                          prev_hash, curr_hash, old_l2m, new_l2m, iso):
    global oldl2m
    global newl2m
    oldl2m = old_l2m
    newl2m = new_l2m
    
    if not go.endswith("/"):
        go = go + "/"
    
    print ' - reading html template ...'
    with open(template_file, 'r') as rf:
        html_string = rf.read()
    
    print ' - appending invdiffs ...'
    html_string = _getty_append_invdiff(html_string, targets, go, prev_hash, curr_hash, iso)
    print ' - import javascript libs ...'
    html_string = _import_js(html_string, fe_path, go)
    print ' - inv txt to html (prev) ...'
    inv_to_html(targets, go, prev_hash)
    print ' - inv txt to html (post) ...'
    inv_to_html(targets, go, curr_hash)
    
    if iso:
        print ' - mixed inv txt to html ...'
        inv_to_html(targets, go, prev_hash + "_" + curr_hash)
        inv_to_html(targets, go, curr_hash + "_" + prev_hash)
    
    print ' - install tooltips and show/hide contents ...'
    html_string = _getty_install_invtips(html_string, commit_msgs, github_link,
                                         prev_hash, curr_hash, go, old_l2m, new_l2m, iso)
    
    print ' - writing to html ...'
    with open(template_file, 'w') as wf:
        wf.write(html_string)


if __name__ == "__main__":
    main()
