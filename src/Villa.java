import java.util.ArrayList;
import java.util.HashMap;
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
import edu.ucsd.getty.diff.Patch;

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
		
		if (args.length == 6) {
			diff_path = args[0];
			target_path = args[1];
			test_path = args[2];
			package_prefix = args[3];
			prev_commit = args[4];
			curr_commit = args[5];
		} else {
			System.out.println("Incorrect number of arguments given");
			System.exit(1);
		}
		
		try {
			System.out.println("Parsing differential file ...\n");
			IInputProcessor diff_processor = new InputDiffProcessor();
			GitDiff git_diff = diff_processor.parseDiff(diff_path, prev_commit, curr_commit);
			Map<String, Integer[]> file_revision_lines = diff_processor.newLinesRevised(git_diff);
			
			System.out.println("\nGetting changed methods (in .java files only, excluding tests) ...\n");
			IMethodRecognizer ast_inspector = new ASTInspector();
			Set<String> exclusion = new HashSet<String>();
			for (String file : file_revision_lines.keySet())
				if (!file.endsWith(".java") || file.startsWith(test_path))
					exclusion.add(file);
			for (String ext : exclusion)
				file_revision_lines.remove(ext);
				
			Set<String> revised_methods = ast_inspector.changedMethods(file_revision_lines);
			System.out.println("changed methods: " + revised_methods + "\n");
			
			System.out.println("\nGetting call graphs and candidate call chains ...\n");
			ITraceFinder chain_generator = new CandidateGenerator(revised_methods, target_path, package_prefix);
			Map<String, Set<List<String>>> candidates = chain_generator.getCandidateTraces();
			
			// TODO: output for filter
			System.out.println(candidates);
			
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(2);
		}
		
	}

}
