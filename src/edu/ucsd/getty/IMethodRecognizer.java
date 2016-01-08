package edu.ucsd.getty;

import java.util.Map;
import java.util.Set;

public interface IMethodRecognizer {
	public Set<String> changedMethods(String targetFolder, Map<String, Integer[]> diffs);
	public Set<String> changedMethods(Map<String, Integer[]> diffs);
}
