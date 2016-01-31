import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import edu.ucsd.getty.IInputProcessor;
import edu.ucsd.getty.IMethodRecognizer;
import edu.ucsd.getty.ITraceFinder;
import edu.ucsd.getty.comp.ASTInspector;
import edu.ucsd.getty.comp.CandidateGenerator;
import edu.ucsd.getty.comp.InputDiffProcessor;
import edu.ucsd.getty.diff.GitDiff;
import edu.ucsd.getty.utils.DataStructureBuilder;
import edu.ucsd.getty.utils.SetOperations;

public class Villa {

	/**
	 * Input: diff file (path), target files (path), excluded test files (path), 
	 * 		  package (prefix) range, previous and current commit hashes
	 * Output: print candidate call chains
	 * @param args
	 * 
	 * FIXME: now it only handles new or revised lines, but deleted lines.
	 */
	public static void main(String[] args) {
		System.out.println("\n*************************************************************");
		System.out.println("Getty Villa: read diff and target files and get method chains");
		System.out.println("*************************************************************\n");
		
		check_args(args);
		
		switch(args[0]) {
		
		/**
		 * simgen=old (DEFAULT, so, s)
		 * simgen=new (sn)
		 */
			case "-s":
			case "-so":
			case "--simgen":
			case "--simgen=old": 
			case "-sn":
			case "--simgen=new":
				execute_tour_simple_mode(args);
				break;
				
		/**
		 * comgen (c)
		 */
			case "-c":
			case "--comgen":
				execute_tour_complex_mode(args);
				break;
			
		/**
		 * unrecognizable execution mode
		 */
			default:
				System.out.println("Unrecognizable first argument (execution mode): " + args[0]);
				print_help_info();
				System.exit(1);
				break;
		}
		
	}

	private static void check_args(String[] args) {
		if (args.length == 0 || args[0].equals("-h") || args[0].equals("--help")) {
			print_help_info();
			System.exit(1);
		} else if (args.length == 7 || args.length == 9) {
			// tour mode argument check
			if (!(args[0].equals("--simgen=old") || args[0].equals("--simgen=new") 
					|| args[0].equals("--simgen") 
					|| args[0].equals("-s") || args[0].equals("-so")
					|| args[0].equals("-c") || args[0].equals("--comgen"))) {
				System.out.println("Incorrect execution mode: " + args[0]);
				print_help_info();
				System.exit(1);
			}
			if (args.length == 9 
					&& !(args[7].equals("-o") || args[7].equals("--output"))) {
				System.out.println("Incorrect secondary option: " + args[7]);
				print_help_info();
				System.exit(1);
			}
//		} else if (args.length == -1) {  // FIXME: get number of args for other mode(s)
//			// TODO: for other Java tools
		} else {
			System.out.println("Incorrect arguments given.");
			print_help_info();
			System.exit(1);
		}
	}
	
	private static void print_help_info() {
		System.out.println("Usage:"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar --help|-h"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--simgen=old | --simgen | -so | -s diffpath targetpath testsrcrelpath pkgprefix | - prevcommit currcommit "
				+ "[--output | -o outputworkdir]"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--simgen=new | -sn diffpath targetpath testsrcrelpath pkgprefix | - prevcommit currcommit "
				+ "[--output | -o outputworkdir]"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--comgen | -c diffpath targetpath testsrcrelpath pkgprefix | - prevcommit currcommit "
				+ "[--output | -o outputworkdir]"
				+ "\n");
	}
	
	/**
	 * simgen=old (DEFAULT, so, s)
	 * simgen=new (sn)
	 * 
	 * The simple mode to generate changed method set*, candidate call chains, 
	 * and all callers in the chains 
	 * 
	 * * In this mode, we consider only the current version
	 */
	protected static void execute_tour_simple_mode(String[] args) {
		String diff_path = args[1];
		String target_path = args[2];
		String test_path = args[3];
		String package_prefix = args[4].equals("-") ? "" : args[4];
		String prev_commit = args[5];
		String curr_commit = args[6];
		
		String output_dir = "/tmp/getty/";
		if (args.length == 9 && (args[7].equals("-o") || args[7].equals("--output"))) {
			output_dir = args[8];
			if(!output_dir.endsWith("/"))
				output_dir += "/";
		}
		
		try {
			/**********************************/
			Map<String, Integer[]> file_revision_lines;
			if (args[0].equals("-s") || args[0].equals("-so") 
					|| args[0].equals("--simgen") || args[0].equals("--simgen=old"))
				file_revision_lines = get_original_file_lines_map(diff_path, prev_commit, curr_commit);
			else  // args[0].equals("-sn") || args[0].equals("--simgen=new")
				file_revision_lines = get_revised_file_lines_map(diff_path, prev_commit, curr_commit);
			
			Set<String> revised_methods = get_changed_methods(test_path, file_revision_lines);
//					System.out.println("changed methods: " + revised_methods + "\n");
			String chgmtd_out_path = output_dir + "_getty_chgmtd_src_";
			if (args[0].equals("-s") || args[0].equals("-so") 
					|| args[0].equals("--simgen") || args[0].equals("--simgen=old"))
				chgmtd_out_path += "old" + "_" + prev_commit + "_.ex";
			else  // args[0].equals("-sn") || args[0].equals("--simgen=new")
				chgmtd_out_path += "new" + "_" + curr_commit + "_.ex";
			System.out.println(
					"<simple mode>: number of changed methods: " + revised_methods.size() + "\n"
					+ "  output to file --> " + chgmtd_out_path + " ...\n");
			output_to(chgmtd_out_path, revised_methods);

			
			/**********************************/
			String this_commit;
			if (args[0].equals("-s") || args[0].equals("-so") 
					|| args[0].equals("--simgen") || args[0].equals("--simgen=old"))
				this_commit = prev_commit;
			else  // args[0].equals("-sn") || args[0].equals("--simgen=new")
				this_commit = curr_commit;
			/**********************************/
			ITraceFinder chain_generator = get_generator(target_path, package_prefix, revised_methods);
			
			Set<String> all_project_methods = chain_generator.getAllProjectMethods();
//					System.out.println(all_project_methods);
			String apm_out_path = output_dir + "_getty_allmtd_src_" + this_commit + "_.ex";
			System.out.println(
					"<simple mode>: number of all methods in project: " + all_project_methods.size() + "\n"
							+ "  output to file --> " + apm_out_path + " ...\n");
			output_to(apm_out_path, all_project_methods);
			
			Map<String, Set<List<String>>> candidates = chain_generator.getCandidateTraces();
//					System.out.println(candidates);
			String ccc_out_path = output_dir + "_getty_ccc_" + this_commit + "_.ex";
			int max_chain_len = 0;
			for (String method : candidates.keySet()) {
				int c_len = candidates.get(method).size();
				if (c_len > max_chain_len)
					max_chain_len = c_len;
			}
			System.out.println(
					"<simple mode>: max size of ccc map: " + candidates.size() + "(methods) x " + max_chain_len + "(chains)\n"
					+ "  output to file --> " + ccc_out_path + " ...\n");
			output_to(ccc_out_path, candidates);
			
			
			/**********************************/
			Set<String> all_callers = get_all_callers(candidates);
//					System.out.println(all_callers);
			String clr_out_path = output_dir + "_getty_clr_" + this_commit + "_.ex";
			System.out.println(
					"<simple mode>: number of possible callers: " + all_callers.size() + "\n"
					+ "  output to file --> " + clr_out_path + " ...\n");
			output_to(clr_out_path, all_callers);
			
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(2);
		}
	}
	
	/**
	 * comgen (c)
	 * 
	 * The complex mode to generate changed method set*, candidate call chains, 
	 * all callers in the chains, and all considered methods
	 * 
	 * * In this mode we consider not only the current version for precision
	 * 
	 * So far this mode only support forward analysis, i.e., from older version to newer.
	 */
	protected static void execute_tour_complex_mode(String[] args) {
		String diff_path = args[1];
		String target_path = args[2];
		String test_path = args[3];
		String package_prefix = args[4].equals("-") ? "" : args[4];
		String prev_commit = args[5];
		String curr_commit = args[6];
		
		String output_dir = "/tmp/getty/";
		if (args.length == 9 && (args[7].equals("-o") || args[7].equals("--output"))) {
			output_dir = args[8];
			if(!output_dir.endsWith("/"))
				output_dir += "/";
		}
		
		try {
			/**********************************/
			Map<String, Integer[]> file_revision_lines = get_revised_file_lines_map(diff_path, prev_commit, curr_commit);
			
			Set<String> revised_methods = get_changed_methods(test_path, file_revision_lines);
//					System.out.println("changed methods: " + revised_methods + "\n");
			String chgmtd_out_path = output_dir + "_getty_chgmtd_src_" + "new" + "_" + curr_commit + "_.ex";
			System.out.println(
					"<complex mode>: number of changed methods: " + revised_methods.size() + "\n"
							+ "  output to file --> " + chgmtd_out_path + " ...\n");
			output_to(chgmtd_out_path, revised_methods);
			// will generate more accurate revised_methods set later, soon
			
			
			/**********************************/
			ITraceFinder chain_generator = get_generator(target_path, package_prefix, revised_methods);
			
			Set<String> all_project_methods = chain_generator.getAllProjectMethods();
//					System.out.println(all_project_methods);
			String apm_out_path = output_dir + "_getty_allmtd_src_" + curr_commit + "_.ex";
			System.out.println(
					"<complex mode>: number of all methods in project: " + all_project_methods.size() + "\n"
							+ "  output to file --> " + apm_out_path + " ...\n");
			output_to(apm_out_path, all_project_methods);
			
			/********more precise revised method set********/
			Set<String> revised_methods_old = DataStructureBuilder.loadSetFrom(
					output_dir + "_getty_chgmtd_src_" + "old" + "_" + prev_commit + "_.ex");
			Set<String> possible_ignored_revised_methods = SetOperations.intersection(revised_methods_old, all_project_methods);
			
			// improved revised_methods
			revised_methods = SetOperations.union(revised_methods, possible_ignored_revised_methods);
			String improved_chgmtd_out_path = output_dir + "_getty_chgmtd_src_" + prev_commit + "_" + curr_commit + "_.ex";
			System.out.println(
					"<complex mode>: IMPROVED, number of changed methods: " + revised_methods.size() + "\n"
							+ "  output to file --> " + improved_chgmtd_out_path + " ...\n");
			output_to(improved_chgmtd_out_path, revised_methods);
			
			// removed methods
			Set<String> removed_methods = SetOperations.difference(revised_methods_old, all_project_methods);
			String removed_chgmtd_out_path = output_dir + "_getty_chgmtd_src_gone_" + prev_commit + "_" + curr_commit + "_.ex";
			System.out.println(
					"<complex mode>: IMPROVED, number of removed methods: " + removed_methods.size() + "\n"
							+ "  output to file --> " + removed_chgmtd_out_path + " ...\n");
			output_to(removed_chgmtd_out_path, removed_methods);
			/************************************************/
			ITraceFinder chain_generator_improved = get_generator(target_path, package_prefix, revised_methods);
			
			Map<String, Set<List<String>>> candidates = chain_generator_improved.getCandidateTraces();
//					System.out.println(candidates);
			String ccc_out_path = output_dir + "_getty_ccc_" + curr_commit + "_.ex";
			int max_chain_len = 0;
			for (String method : candidates.keySet()) {
				int c_len = candidates.get(method).size();
				if (c_len > max_chain_len)
					max_chain_len = c_len;
			}
			System.out.println(
					"<complex mode>: max size of ccc map: " + candidates.size() + "(methods) x " + max_chain_len + "(chains)\n"
							+ "  output to file --> " + ccc_out_path + " ...\n");
			output_to(ccc_out_path, candidates);
			
			
			/**********************************/
			Set<String> all_callers = get_all_callers(candidates);
//					System.out.println(all_callers);
			String clr_out_path = output_dir + "_getty_clr_" + curr_commit + "_.ex";
			System.out.println(
					"<complex mode>: number of possible callers: " + all_callers.size() + "\n"
							+ "  output to file --> " + clr_out_path + " ...\n");
			output_to(clr_out_path, all_callers);
			
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(2);
		}
	}
	
	private static void output_to(String out_path, Set<String> set_content) throws IOException {
		PrintWriter out_file = new PrintWriter(
				new BufferedWriter(new FileWriter(out_path, false)));
		String str_content = "[";
		for (String method : set_content) {
			str_content += ("\"" + method + "\", ");
		}
		str_content += "]";
		out_file.print(str_content);
		out_file.close();
	}
	
	private static void output_to(String out_path, Map<String, Set<List<String>>> ccc_content) throws IOException {
		PrintWriter out_file = new PrintWriter(
				new BufferedWriter(new FileWriter(out_path, false)));
		String str_content = "{";
		for (String method : ccc_content.keySet()) {
			str_content += ("\"" + method + "\": [");
			for (List<String> chain : ccc_content.get(method)) {
				str_content += "[";
				for (String mtd : chain) {
					str_content += ("\"" + mtd + "\", ");
				}
				str_content += "], ";
			}
			str_content += "], ";
		}
		str_content += "}";
		out_file.print(str_content);
		out_file.close();
	}

	private static Set<String> get_all_callers(Map<String, Set<List<String>>> candidates) {
		System.out.println("\nGetting all callers of changed methods from ccc ...\n");
		Set<String> all_callers = new HashSet<String>();
		for (String method : candidates.keySet()) {
			for (List<String> chain : candidates.get(method)) {
				for (String mtd : chain) {
					if (!mtd.equals("!") && !mtd.startsWith("@"))
						all_callers.add(mtd);
				}
			}
		}
		return all_callers;
	}
	
	private static ITraceFinder get_generator(String target_path, String package_prefix, Set<String> revised_methods) {
		System.out.println("\nGetting all project methods, call graphs and candidate call chains ...\n");
		ITraceFinder chain_generator = new CandidateGenerator(revised_methods, target_path, package_prefix);
		return chain_generator;
	}

	private static Set<String> get_changed_methods(String test_path, Map<String, Integer[]> file_revision_lines) {
		System.out.println("\nGetting changed methods (in .java files only, excluding tests) ...\n");
		IMethodRecognizer ast_inspector = new ASTInspector();
		Set<String> exclusion = new HashSet<String>();
		for (String file : file_revision_lines.keySet())
			if (!file.endsWith(".java") || file.startsWith(test_path))
				exclusion.add(file);
		for (String ext : exclusion)
			file_revision_lines.remove(ext);
			
		Set<String> revised_methods = ast_inspector.changedMethods(file_revision_lines);
		return revised_methods;
	}

	private static Map<String, Integer[]> get_revised_file_lines_map(String diff_path, String prev_commit, String curr_commit)
			throws Exception {
		System.out.println("Parsing differential file for the revised ...\n");
		IInputProcessor diff_processor = new InputDiffProcessor();
		GitDiff git_diff = diff_processor.parseDiff(diff_path, prev_commit, curr_commit);
		Map<String, Integer[]> file_revision_lines = diff_processor.newLinesRevised(git_diff);
		return file_revision_lines;
	}
	
	private static Map<String, Integer[]> get_original_file_lines_map(String diff_path, String prev_commit, String curr_commit)
			throws Exception {
		System.out.println("Parsing differential file for the original ...\n");
		IInputProcessor diff_processor = new InputDiffProcessor();
		GitDiff git_diff = diff_processor.parseDiff(diff_path, prev_commit, curr_commit);
		Map<String, Integer[]> file_revision_lines = diff_processor.oldLinesRevised(git_diff);
		return file_revision_lines;
	}

}
