package edu.ucsd.getty;

import java.util.Map;
import java.util.Set;

public interface IMethodRecognizer {
	public Map<String, String> l2m();
	public Map<String, Set<String>> m2l();
	public Set<String> changedMethods(String targetFolder, Map<String, Integer[]> diffs);
	public Set<String> changedMethods(Map<String, Integer[]> diffs);
}
