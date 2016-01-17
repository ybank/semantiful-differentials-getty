package edu.ucsd.getty.callgraph;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class NameHandler {

	// exclude anonymous classes
	private static Pattern classExclusionPattern = Pattern.compile(".*\\$\\d+.*");
	
	// exclude access$X00 methods for accessing outer class' field
	private static Pattern methodExclusionPattern = Pattern.compile(".*access\\$\\d+");
	
	// method string pattern
	private static Pattern methodNamePattern = Pattern.compile("(.*):(.*)");
	
	public static boolean shallExcludeClass(String target) {
		Matcher m = classExclusionPattern.matcher(target);
		return m.matches();
	}
	
	public static boolean shallExcludeMethod(String target) {
		Matcher m = methodExclusionPattern.matcher(target);
		return m.matches();
	}
	
	public static String extractClassName(String methodname) {
		Matcher m = methodNamePattern.matcher(methodname);
		if (m.find() && m.groupCount() == 2) {
			return m.group(1);
		} else
			return null;
	}
	
	public static String extractMethodName(String methodname) {
		Matcher m = methodNamePattern.matcher(methodname);
		if (m.find() && m.groupCount() == 2) {
			return m.group(2);
		} else
			return null;
	}

}
