package edu.ucsd.getty.utils;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

public class DataStructureBuilder {

	public static Set<String> loadSetFrom(String path) {
		// this method process a single line (the first line) that represents a set of method names
		BufferedReader dsfile;
		try {
			dsfile = new BufferedReader(new FileReader(path));
			String setstring = dsfile.readLine().trim();  // only process the first line
			dsfile.close();
			
			if (setstring.length() == 0 || !setstring.startsWith("[") || !setstring.endsWith("]"))
				throw new Exception("malformated set string: it should start with [ and end with ]");
			
			Set<String> targets = new HashSet<String>();
			if (setstring.length() == 2)
				return targets;
			else {
				String[] target_strings = setstring.substring(1, setstring.length()-1).split(", ");
				for (String ts : target_strings)
					if (ts.startsWith("\"") && ts.endsWith("\""))
						targets.add(ts.substring(1, ts.length()-1));
					else
						throw new Exception("malformated set string: each target should start and end with \"");
			}
			
			return targets;
			
		} catch (FileNotFoundException fnfe) {
			fnfe.printStackTrace();
			System.exit(10);
		} catch (IOException ioe) {
			ioe.printStackTrace();
			System.exit(11);
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(12);
		}
		return null;
	}
	
}
