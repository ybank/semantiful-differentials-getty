package edu.ucsd.getty.diff;

import java.util.ArrayList;
import java.util.List;

public class GitDiff {

	private final String commitHash;
	private final String parentHash;

	private List<Patch> patches;
	
	public GitDiff(String parentHash, String commitHash) {
		this.parentHash = parentHash;
		this.commitHash = commitHash;
		patches = new ArrayList<Patch>();
	}
	
	public GitDiff() {
		this(null, null);
	}
	
	public void addPatch(Patch patch) {
		this.patches.add(patch);
	}
	
	public void addPatches(List<Patch> patches) {
		this.patches.addAll(patches);
	}

	public String getCommitHash() {
		return this.commitHash;
	}
	
	public String getParentHash() {
		return parentHash;
	}

	public List<Patch> getPatches() {
		return this.patches;
	}
	
	public Patch getLastPatch() throws IndexOutOfBoundsException {
		if (patches.isEmpty())
			throw new IndexOutOfBoundsException("no patches are in this diff");
		else
			return patches.get(patches.size() - 1);
	}
	
}
