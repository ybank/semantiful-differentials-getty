# all Daikon's usage for invariant analysis

from misc import *
from utils import *


# the main entrance
def visit(prev_hash, post_hash, \
          old_changed_methods, \
          old_all_callers, old_all_cccs, old_all_methods, \
          new_changed_methods, new_improved_changed_methods, new_removed_changed_methods, \
          new_all_callers, new_all_cccs, new_all_methods):
    
    # DEBUG ONLY
    print common_prefixes(old_all_methods)
    print formalize(common_prefixes(old_all_methods))
    print common_prefixes(new_all_methods)
    print formalize(common_prefixes(new_all_methods))
    
    
