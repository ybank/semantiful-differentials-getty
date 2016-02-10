from tools.hdiff import diff_to_html, getty_append_invdiff
from tools.os import sys_call


def view(pwd, go, prev_hash, post_hash, targets):
    diff_in = pwd[:-1] + ".__getty_output__/text.diff"
    html_out = pwd[:-1] + ".__getty_output__/sema.diff.html"
    diff_to_html(diff_in, html_out, exclude_headers=False)
    getty_append_invdiff(html_out, targets, go, prev_hash, post_hash)
    
    # open with Safari on Mac OS
    sys_call("open -a /Applications/Safari.app/Contents/MacOS/Safari " + html_out)
#     # open with default app
#     sys_call("open " + html_out)
