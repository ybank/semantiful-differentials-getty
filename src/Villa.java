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
		
		if (args.length == 0 || args[0].equals("-h") || args[0].equals("--help")) {
			print_help_info();
			System.exit(1);
		} else if (args.length != 7 && args.length != 9) {
			System.out.println("Incorrect (number of) arguments given");
			print_help_info();
			System.exit(1);
		}
		
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
		
		switch(args[0]) {
		
		/**
		 * simgen=old (so)
		 * simgen=new (sn, s)
		 * 
		 * The simple mode to generate changed method set*, candidate call chains, 
		 * and all callers in the chains 
		 * 
		 * * In this mode, we consider only the current version
		 */
			case "-so":
			case "--simgen=old":
			case "-s": 
			case "-sn":
			case "--simgen=new":
				try {
					Map<String, Integer[]> file_revision_lines = get_revised_file_lines_map(diff_path, prev_commit, curr_commit);
					
					Set<String> revised_methods = get_changed_methods(test_path, file_revision_lines);
//					System.out.println("changed methods: " + revised_methods + "\n");
					String chgmtd_out_path = output_dir + "_getty_chgmtd_src_";
					if (args[0].equals("-so") || args[0].equals("--simgen=old"))
						chgmtd_out_path += "old" + "_" + prev_commit + "_.ex";
					else
						chgmtd_out_path += "new" + "_" + curr_commit + "_.ex";
					System.out.println(
							"number of changed methods: " + revised_methods.size() + "\n"
							+ "  output to file --> " + chgmtd_out_path + " ...\n");
					output_to(chgmtd_out_path, revised_methods);

					
					ITraceFinder chain_generator = get_generator(target_path, package_prefix, revised_methods);
					
					Map<String, Set<List<String>>> candidates = chain_generator.getCandidateTraces();
//					System.out.println(candidates);
					String ccc_out_path = output_dir + "_getty_ccc_" + curr_commit + "_.ex";
					int max_chain_len = 0;
					for (String method : candidates.keySet()) {
						int c_len = candidates.get(method).size();
						if (c_len > max_chain_len)
							max_chain_len = c_len;
					}
					System.out.println(
							"max size of ccc map: " + candidates.size() + "(methods) x " + max_chain_len + "(chains)\n"
							+ "  output to file --> " + ccc_out_path + " ...\n");
					output_to(ccc_out_path, candidates);
					
					Set<String> all_project_methods = chain_generator.getAllProjectMethods();
//					System.out.println(all_project_methods);
					String apm_out_path = output_dir + "_getty_allmtd_src_" + curr_commit + "_.ex";
					System.out.println(
							"number of all methods in project: " + all_project_methods.size() + "\n"
							+ "  output to file --> " + apm_out_path + " ...\n");
					output_to(apm_out_path, all_project_methods);
					
					
					Set<String> all_callers = get_all_callers(candidates);
//					System.out.println(all_callers);
					String clr_out_path = output_dir + "_getty_clr_" + curr_commit + "_.ex";
					System.out.println(
							"number of possible callers: " + all_callers.size() + "\n"
							+ "  output to file --> " + clr_out_path + " ...\n");
					output_to(clr_out_path, all_callers);
					
				} catch (Exception e) {
					e.printStackTrace();
					System.exit(2);
				}
				break;
			
			/**
			 * comgen=forward (cf, c)
			 * comgen=backward (cb)
			 * 
			 * The complex mode to generate changed method set*, candidate call chains, 
			 * all callers in the chains, and all considered methods
			 * 
			 * * In this mode we consider not only the current version for precision
			 */
			case "-c":
			case "-cf":
			case "--comgen=forward":
			case "-cb":
			case "--comgen=backward":
				try {
					// FIXME: more accurate changed methods
					
				} catch (Exception e) {
					e.printStackTrace();
					System.exit(2);
				}
				break;
			default:
				System.out.println("Incorrect (number of) arguments given");
				System.exit(1);
				break;
		}
		
	}

	private static void print_help_info() {
		System.out.println("Usage:"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar --help|-h"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--simgen=new|-sn|-s diffpath targetpath testsrcrelpath pkgprefix|- prevcommit currcommit "
				+ "[--output|-o outputworkdir]"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--simgen=old|-so diffpath targetpath testsrcrelpath pkgprefix|- prevcommit currcommit "
				+ "[--output|-o outputworkdir]"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--comgen=forward|-cf|-c diffpath targetpath testsrcrelpath pkgprefix|- prevcommit currcommit "
				+ "[--output|-o outputworkdir]"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--comgen=backward|-cb diffpath targetpath testsrcrelpath pkgprefix|- prevcommit currcommit "
				+ "[--output|-o outputworkdir]"
				+ "\n");
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
