# this file contains all config paras
import multiprocessing

# default junit version to use uniformly
default_junit_version = "4.12-getty"
use_special_junit_for_dyn = True
special_junit_version = "4.11"

# whether to infer invariants for tests
analyze_tests = True

# whether to limit interested into a relatively smaller set
limit_interest = True
limit_distance = 3

# scale parameters
num_master_workers = 1
auto_fork = True
num_slave_workers = multiprocessing.cpu_count()
classes_per_fork = 1
min_heap = "2048m"
max_heap = "16384m"

# options to control Daikon analysis
omit_redundant_invs = True
daikon_format_only = True
disable_known_invs = False

# whether to use compressed inv file
compress_inv = False

# development options
show_debug_info = True
show_debug_details = False

# misc
review_after_analysys = False
