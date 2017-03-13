# this file contains all config paras
import multiprocessing, time

# default junit version to use uniformly
default_junit_version = "4.13-getty"
use_special_junit_for_dyn = False
special_junit_version = "4.11"

# whether to infer invariants for tests
analyze_tests = True
analyze_less_tests = True

# whether to limit interested into a relatively smaller set
limit_interest = True
limit_distance = 3
class_level_expansion = True
expansion_tmp_files = "_getty_temp_expansion_targets_"
further_expansion_analysis = False  # if true, consider to improve UI elements

# scale parameters
num_master_workers = 1
auto_fork = True
num_slave_workers = multiprocessing.cpu_count()
classes_per_fork = 1
min_heap = "4096m"
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
blocked_daikon_invs_exp = compose_block_daikon_invs_exp(blocked_daikon_invs)
output_inv_format = "Daikon"

# whether to use compressed inv file
compress_inv = False

# development options
show_debug_info = True
show_debug_details = False
show_regex_debug = True
show_stack_trace_info = False

# effortless mvn setup
no_mvn_customization = True  # BETA
effortless_mvn_setup = False

# include test coverage report
analyze_test_coverage = False

# profile performance
profile_performance = False

# review options
git_diff_extra_ops = "-b --ignore-blank-lines"
review_auto_open = False
install_extra_tips = False
install_inv_tips = False
install_diffinv_only = True
jump_to_method = True
max_context_line = 65536
max_diff_lines = 1000
max_diff_line_size = 1000
inv_diff_context_lines = 0
change_alignment = True
similarity_bar = 0.8
the_common_package = []  # NOT read-only: change after info path
hidden_package_names = ["java.lang"]
extreme_simple_mode = True

# method information file line prefix
method_info_line_prefix = "[GETTY-JAVACG-METHOD-INFO] "
max_method_decl_span = 5

# misc
version_time = str(int(time.time()))
use_tmp_files = False
