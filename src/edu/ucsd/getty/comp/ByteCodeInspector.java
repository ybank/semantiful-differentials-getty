package edu.ucsd.getty.comp;

import java.util.Map;
import java.util.Set;

import edu.ucsd.getty.IMethodRecognizer;

public class ByteCodeInspector implements IMethodRecognizer {

	// TODO implememt these if needed, but be careful when multiple classes are created by one source
	
	@Override
	public Set<String> changedMethods(String targetFolder, Map<String, Integer[]> diffs) {
		// TODO Auto-generated method stub
		return null;
	}
	
	@Override
	public Set<String> changedMethods(Map<String, Integer[]> diffs) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Map<String, String> l2m() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Map<String, Set<String>> m2l() {
		// TODO Auto-generated method stub
		return null;
	}

}
