# this file contains all config paras

# default junit version to use uniformly
default_junit_version = "4.12-getty"
use_special_junit_for_dyn = True
special_junit_version = "4.11"

# whether to infer invariants for tests
analyze_tests = True

# whether to limit interested into a relatively smaller set
limit_interest = True
limit_distance = 2

# scale parameters
num_workers = 1
auto_fork = True
classes_per_fork = 2
min_heap = "2048m"
max_heap = "16384m"
