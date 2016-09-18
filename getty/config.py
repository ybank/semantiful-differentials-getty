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
limit_distance = 0

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
blocked_daikon_invs = [
    "daikon.inv.ternary.threeScalar.LinearTernary.enabled",
    "daikon.inv.ternary.threeScalar.LinearTernaryFloat.enabled"]
def compose_block_daikon_invs_exp(blacklist):
    exps = []
    for blackout in blacklist:
        exps.append("--config_option " + blackout + "=false")
    return " ".join(exps)
blacked_daikon_invs_exp = compose_block_daikon_invs_exp(blocked_daikon_invs)

# whether to use compressed inv file
compress_inv = False

# development options
show_debug_info = True
show_debug_details = False

# include test coverage report
analyze_test_coverage = False

# profile performance
profile_performance = True

# misc
max_diff_lines = 1000
max_diff_line_size = 1000
install_inv_tips = False
install_diffinv_only = True
review_with_src = True
review_after_analysys = False
