# profiling functionalities

import cProfile
import pstats


def run_and_report(cmd2run, report_file):
    cProfile.run(cmd2run, report_file)
    with open(report_file+".readable", "w") as human_readable_file:
        p = pstats.Stats(report_file, stream=human_readable_file)
        p.strip_dirs().sort_stats('cumtime').print_stats(10)


def log_csv(titles, list_data_list, filename):
    with open(filename, 'w') as wf:
        wf.write(",".join(titles) + "\n")
        for data_list in list_data_list:
            wf.write(",".join([str(x) for x in data_list]) + "\n")
