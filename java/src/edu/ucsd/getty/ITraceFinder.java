package edu.ucsd.getty;

import java.util.List;
import java.util.Map;
import java.util.Set;

public interface ITraceFinder {

	public Set<String> getCallersFor(String methodName);
	public Set<String> getCallersFor(Set<String> methodNames);
	public Set<List<String>> getCandidateTraces(String methodName);
	public Map<String, Set<List<String>>> getCandidateTraces(Set<String> methods);
	public Map<String, Set<List<String>>> getCandidateTraces();
	public Set<String> getAllProjectMethods();
	public Set<String> getCalleesFor(String methodName);
	public Set<String> getCalleesFor(Set<String> methodNames);
	public Map<String, Map<String, Set<String>>> possibleOuterStreams();
	public Map<String, Set<String>> possibleInnerStreams();
	
}
