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
		
		String diff_path = null;
		String target_path = null;
		String test_path = null;
		String package_prefix = null;
		String prev_commit = null;
		String curr_commit = null;
		String old_srcpath = null;
		String output_dir = null;
		
		if (args.length < 1 || args[0].equals("-h") || args[0].equals("--help")) {
			print_help_info();
			System.exit(1);
		}
		
		switch(args[0]) {
			case "-s":
			case "--simgen":
				if (args.length != 7 && args.length != 9) {
					System.out.println("Incorrect (number of) arguments given");
					print_help_info();
					System.exit(1);
				}
				diff_path = args[1];
				target_path = args[2];
				test_path = args[3];
				package_prefix = args[4];
				prev_commit = args[5];
				curr_commit = args[6];
				if (args.length == 9 && (args[7].equals("-o") || args[7].equals("--output"))) {
					output_dir = args[8];
					if(!output_dir.endsWith("/"))
						output_dir += "/";
				} else {
					output_dir = "/tmp/getty/";
				}
				try {
					Map<String, Integer[]> file_revision_lines = get_revised_file_lines_map(diff_path, prev_commit, curr_commit);
					
					Set<String> revised_methods = get_changed_methods(test_path, file_revision_lines);
//					System.out.println("changed methods: " + revised_methods + "\n");
					String chgmtd_out_path = output_dir + "_getty_chgmtd_src_" + prev_commit + "_" + curr_commit + "_.ex";
					System.out.println("number of changed methods: " + revised_methods.size() + "\n"
							+ "  output to file " + chgmtd_out_path + " ...\n");
					output_to(chgmtd_out_path, revised_methods);
					
					Map<String, Set<List<String>>> candidates = get_candidates(target_path, package_prefix, revised_methods);
//					System.out.println(candidates);
					String ccc_out_path = output_dir + "_getty_ccc_" + curr_commit + "_.ex";
					System.out.println("size of ccc map: " + candidates.size() + "\n"
							+ "  output to file " + ccc_out_path + " ...\n");
					output_to(ccc_out_path, candidates);
					
				} catch (Exception e) {
					e.printStackTrace();
					System.exit(2);
				}
				break;
			case "-c":
			case "--comgen":
				if (args.length != 8 && args.length != 10) {
					System.out.println("Incorrect (number of) arguments given");
					print_help_info();
					System.exit(1);
				}
				diff_path = args[1];
				target_path = args[2];
				test_path = args[3];
				package_prefix = args[4];
				prev_commit = args[5];
				curr_commit = args[6];
				old_srcpath = args[7];
				if (args.length == 10 && (args[8].equals("-o") || args[8].equals("--output"))) {
					output_dir = args[9];
					if(!output_dir.endsWith("/"))
						output_dir += "/";
				} else {
					output_dir = "/tmp/getty/";
				}
				try {
					// FIXME: more accurate changed methods
					
					Map<String, Integer[]> old_file_revision_lines = get_original_file_lines_map(diff_path, prev_commit, curr_commit);
					Map<String, Integer[]> file_revision_lines = get_revised_file_lines_map(diff_path, prev_commit, curr_commit);
					
					// TODO: more steps ...
					
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

	private static void print_help_info() {
		System.out.println("Usage:"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--simgen|-s diffpath targetpath testpath pkgprefix prevcommit currcommit "
				+ "[--output|-o outputworkdir]"
				+ "\n\t  "
				+ "java -jar Getty.Villa.jar "
				+ "--comgen|-c diffpath targetpath testpath pkgprefix prevcommit currcommit oldbinpath "
				+ "[--output|-o outputworkdir]"
				+ "\n");
	}

	private static Map<String, Set<List<String>>> get_candidates(String target_path, String package_prefix,
			Set<String> revised_methods) {
		System.out.println("\nGetting call graphs and candidate call chains ...\n");
		ITraceFinder chain_generator = new CandidateGenerator(revised_methods, target_path, package_prefix);
		Map<String, Set<List<String>>> candidates = chain_generator.getCandidateTraces();
		return candidates;
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
