package edu.ucsd.getty;

import java.util.List;
import java.util.Map;

import edu.ucsd.getty.diff.GitDiff;

public interface IInputProcessor {
	public GitDiff parseDiffString(String diffs) throws Exception;
	public GitDiff parseDiffString(String diffs, String parentHash, String currentHash) throws Exception;
	public GitDiff parseDiff(String diffPath) throws Exception;
	public GitDiff parseDiff(String diffPath, String parentHash, String currentHash) throws Exception;
	public Map<String, Integer> oldPatchRange(GitDiff diff);
	public Map<String, Integer> newPatchRange(GitDiff diff);
	public Map<String, Integer[]> oldLinesRevised(GitDiff diff);
	public Map<String, Integer[]> newLinesRevised(GitDiff diff);
}
