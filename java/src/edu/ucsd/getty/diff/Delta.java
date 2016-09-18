package edu.ucsd.getty.diff;

import java.util.List;

public abstract class Delta {
	
	private Chunk original;
	private Chunk revised;
	
	private List<String> details;
	
	public static enum TYPE {
		INSERT, DELETE, MODIFY;
	}
	
	public Delta(Chunk original, Chunk revised, List<String> details) {
		this.original = original;
		this.revised = revised;
		this.details = details;
	}
	
	public abstract TYPE getType();
	
	public Chunk getOriginal() {
		return this.original;
	}
	
	public Chunk getRevised() {
		return this.revised;
	}
	
	public List<String> getDetails() {
		return this.details;
	}
}
