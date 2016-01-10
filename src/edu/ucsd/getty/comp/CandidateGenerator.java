package edu.ucsd.getty.comp;

import java.util.Set;

import edu.ucsd.getty.ITraceFinder;

public class CandidateGenerator implements ITraceFinder {
	
	private Set<String> changedMethods;

	public CandidateGenerator(Set<String> methods) {
		// TODO Auto-generated constructor stub
	}

	@Override
	public Set<String> getCallers(String methodName) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Set<String> getCallers(Set<String> methodNames) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Set<String[]> getTraces(String methodName) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Set<String[]> getCandidateTraces(Set<String> methods) {
		// TODO Auto-generated method stub
		return null;
	}

}
