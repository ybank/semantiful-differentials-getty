package edu.ucsd.getty;

import java.util.Set;

public interface ITraceFinder {

	public Set<String> getCallers(String methodName);
	public Set<String> getCallers(Set<String> methodNames);
	public Set<String[]> getTraces(String methodName);
	public Set<String[]> getCandidateTraces(Set<String> methods);
	
}
