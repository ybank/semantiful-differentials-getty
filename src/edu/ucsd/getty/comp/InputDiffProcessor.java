package edu.ucsd.getty.comp;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import edu.ucsd.getty.IInputProcessor;
import edu.ucsd.getty.diff.Chunk;
import edu.ucsd.getty.diff.CreatePatch;
import edu.ucsd.getty.diff.DeletaDelta;
import edu.ucsd.getty.diff.Delta;
import edu.ucsd.getty.diff.GitDiff;
import edu.ucsd.getty.diff.InsertDelta;
import edu.ucsd.getty.diff.ModifyDelta;
import edu.ucsd.getty.diff.Patch;
import edu.ucsd.getty.diff.UpdatePatch;
import edu.ucsd.getty.diff.RemovePatch;
import edu.ucsd.getty.diff.caches.DeltaCache;
import edu.ucsd.getty.diff.caches.PatchCache;

public class InputDiffProcessor implements IInputProcessor {

	protected static enum STATUS {
		READY,  // to PATCH_HEADER, from DELTA_BODY
		PATCH_HEADER,  // to HEADER_COMPLETION/self, from READY/self
		HEADER_COMPLETION,  // to DELTA_UNIT, from PATCH_HEADER
		DELTA_UNIT,  // to DELTA_HEADER_SET, from HEADER_COMPLETION
		DELTA_HEADER_SET,  // to DELTA_BODY, from DELTA_UNIT/DELTA_BODY
		DELTA_BODY;  // to DELTA_HEADER_SET/READY/self, from DELTA_HEADER_SET/self
	}
	
	private STATUS status;
	
	public InputDiffProcessor() {
		this.status = STATUS.READY;
	}
	
	public void reset() {
		this.status = STATUS.READY;
	}
	
	@Override
	public GitDiff parseDiffString(String diffs) throws Exception {
		return this.parseDiffString(diffs, null, null);
	}

	@Override
	public GitDiff parseDiffString(String diffs, String parentHash, String currentHash) throws Exception {
		if (this.status != STATUS.READY)
			throw new Exception("the processor is not ready");
		String[] diffLinesArray = diffs.split("\n");
		List<String> diffLines = new ArrayList<String>(diffLinesArray.length);
		Collections.addAll(diffLines, diffLinesArray);
		GitDiff diff = modelDiff(diffLines, parentHash, currentHash);
		return diff;
	}
	
	@Override
	public GitDiff parseDiff(String diffPath) throws Exception {
		return this.parseDiff(diffPath, null, null);
	}

	@Override
	public GitDiff parseDiff(String diffPath, String parentHash, String currentHash) throws Exception {
		if (this.status != STATUS.READY)
			throw new Exception("the processor is not ready");
		List<String> diffLines = fileToLines(diffPath);
		GitDiff diff = modelDiff(diffLines, parentHash, currentHash);
		return diff;
	}

	public GitDiff modelDiff(List<String> diffLines, String parentHash, String currentHash) throws Exception {
		
		if (this.status != STATUS.READY)
			throw new Exception("the processor is not ready");
		
		if (diffLines.size() <= 1)
			throw new Exception("there is no difference");
		
		GitDiff diff = new GitDiff(parentHash, currentHash);
		PatchCache currentPatchCache = new PatchCache();
		DeltaCache currentDeltaCache = new DeltaCache();
		
		for (String line : diffLines) {
			switch(status) {
				case READY:
					readAtReady(line, currentPatchCache);
					break;
				case PATCH_HEADER:
					read4PatchHeader(line, currentPatchCache);
					break;
				case HEADER_COMPLETION:
					read3Pluses(line, currentPatchCache, diff);
					break;
				case DELTA_UNIT:
					read2Ats(line, currentPatchCache, currentDeltaCache);
					break;
				case DELTA_HEADER_SET:
					readInitialDeltaLine(line, currentDeltaCache);
					break;
				case DELTA_BODY:
					readDeltaLine(line, diff, currentPatchCache, currentDeltaCache);
					break;
				default:
					throw new Exception("unknown or unhandled status: " + status.name());						
			}
		}  // END FOR LOOP HERE
		
		// at last, finish creating the last delta and its patch
		finalizeDiff(diff, currentPatchCache, currentDeltaCache);
		
		return diff;
	}

	private void readAtReady(String line, PatchCache currentPatchCache) throws Exception {
		// in READY
		currentPatchCache.reset();;
		
		Pattern p = Pattern.compile("diff --git a/(.*) b/(.*)");
		Matcher m = p.matcher(line);
		if (m.find() && m.groupCount() == 2) {
			currentPatchCache.aPath = m.group(1);
			currentPatchCache.bPath = m.group(2);
			currentPatchCache.header.addHeaderLine(line);
			status = STATUS.PATCH_HEADER;
		} else {
			throw new Exception("parsing \"diff --git\" ERROR: " + line);
		}
	}

	private void read4PatchHeader(String line, PatchCache currentPatchCache) throws Exception {
		// in PATCH_HEADER
		if (line.startsWith("--- ")) {
			Pattern p = Pattern.compile("--- (.*)");
			Matcher m = p.matcher(line);
			if (m.find() && m.groupCount() == 1) {
				String newPath = m.group(1);
				String possibleNewAPath = newPath.substring(2);
				if (newPath.startsWith("a/")) {
					currentPatchCache.aPath = possibleNewAPath;
				} else if (newPath.equals("/dev/null")) {
					if (currentPatchCache.level == PatchCache.LEVEL.DEFAULT) {
						currentPatchCache.level = PatchCache.LEVEL.CRE;
						currentPatchCache.aPath = null;
					} else {
						throw new Exception("Patch level should be DEFAULT when parsing ---");
					}
				} else {
					throw new Exception("Error at status: " + status.name() + " when parsing: " + line);
				}
			}
			currentPatchCache.header.addHeaderLine(line);
			status = STATUS.HEADER_COMPLETION;
		} else {
			currentPatchCache.header.addHeaderLine(line);
			// keep status
		}
	}

	private void read3Pluses(String line, PatchCache currentPatchCache, GitDiff diff) throws Exception {
		// in HEADER_COMPLETION
		if (line.startsWith("+++")) {
			Pattern p = Pattern.compile("\\+\\+\\+ (.*)");
			Matcher m = p.matcher(line);
			if (m.find() && m.groupCount() == 1) {
				String newPath = m.group(1);
				String possibleNewBPath = newPath.substring(2);
				if (newPath.startsWith("b/")) {
					currentPatchCache.bPath = possibleNewBPath;
					if (currentPatchCache.level == PatchCache.LEVEL.DEFAULT)
						currentPatchCache.level = PatchCache.LEVEL.UPD;
				} else if (newPath.equals("/dev/null")) {
					if (currentPatchCache.level == PatchCache.LEVEL.DEFAULT) {
						currentPatchCache.level = PatchCache.LEVEL.REM;
						currentPatchCache.bPath = null;
					} else
						throw new Exception("Excepting DEFAULT level cache when seeing +++ in line: " + line 
								+ " but was " + currentPatchCache.level);
				} else {
					throw new Exception("Error (unexpected match) at status: " + status.name() + " when parsing: " + line);
				}
			} else {
				throw new Exception("Error (no matching) at status: " + status.name() + " when parsing: " + line);
			}
			currentPatchCache.header.addHeaderLine(line);
			
			// finalize header for this patch
			currentPatchCache.header.completion();
			
			// set up Patch using the cache
			Patch currentPatch;
			switch (currentPatchCache.level) {
				case DEFAULT:
					throw new Exception("type of patch is yet unknown or not set");
				case CRE:
					currentPatch = new CreatePatch(
							currentPatchCache.aPath, currentPatchCache.bPath, currentPatchCache.header);
					break;
				case REM:
					currentPatch = new RemovePatch(
							currentPatchCache.aPath, currentPatchCache.bPath, currentPatchCache.header);
					break;
				case UPD:
					currentPatch = new UpdatePatch(
							currentPatchCache.aPath, currentPatchCache.bPath, currentPatchCache.header);
					break;
				default:
					throw new Exception("unhandled patch cache level");
			}
			
			// add patch to diff
			diff.addPatch(currentPatch);
			
			status = STATUS.DELTA_UNIT;
		} else {
			throw new Exception("Error at status: " + status.name() + " Expecting +++ after ---, but was " + line);
		}
	}

	private void read2Ats(String line, PatchCache currentPatchCache, DeltaCache currentDeltaCache) throws Exception {
		// in DELTA_UNIT
		if (line.startsWith("@@ ")) {
			Pattern p = Pattern.compile("@@ -(.*) \\+(.*) @@.*");
			Matcher m = p.matcher(line);
			if (m.find() && m.groupCount() == 2) {
				currentDeltaCache.reset();
				
				switch (currentPatchCache.level) {
					case DEFAULT:
						throw new Exception("expecting non-default level in currentPatchCache");
					case CRE:
						currentDeltaCache.level = DeltaCache.LEVEL.ADD;
						break;
					case REM:
						currentDeltaCache.level = DeltaCache.LEVEL.SUB;
						break;
					case UPD:
						currentDeltaCache.level = DeltaCache.LEVEL.MIX;
						break;
					default:
						throw new Exception("unhandled patch cache level in status: " + status.name());
				}
				
				String originalMeta = m.group(1);
				if (!originalMeta.contains(","))
					originalMeta = originalMeta + ",0";
				String[] originalNumbers = originalMeta.split(",");
				int originalPos = Integer.parseInt(originalNumbers[0]);
				currentDeltaCache.originalPosition = originalPos;
				int originalRng = Integer.parseInt(originalNumbers[1]);
				currentDeltaCache.originalRange = originalRng;
				
				String revisedMeta = m.group(2);
				if (!revisedMeta.contains(","))
					revisedMeta = revisedMeta + ",0";
				String[] revisedNumbers = revisedMeta.split(",");
				int revisedPos = Integer.parseInt(revisedNumbers[0]);
				currentDeltaCache.revisedPosition = revisedPos;
				int revisedRng = Integer.parseInt(revisedNumbers[1]);
				currentDeltaCache.revisedRange = revisedRng;
				
				currentDeltaCache.details.add(line);
				
				status = STATUS.DELTA_HEADER_SET;
			} else {
				throw new Exception("no match that starts with @@\\space");
			}
		} else {
			throw new Exception("expecting @@ in status " + status.name() + " but was: " + line);
		}
	}

	private void readInitialDeltaLine(String line, DeltaCache currentDeltaCache) throws Exception {
		// in DELTA_HEADER_SET
		switch (line.substring(0, 1)) {
			case " ":
			case "+":
			case "-":
				currentDeltaCache.details.add(line);
				status = STATUS.DELTA_BODY;
				break;
			case "\\":
				status = STATUS.DELTA_BODY;
				break;
			default:
				throw new Exception("unexpected line (with unusual start character): " + line);
		}
	}

	private void readDeltaLine(String line, GitDiff diff, PatchCache currentPatchCache, DeltaCache currentDeltaCache) throws Exception {
		// in DELTA_BODY
		switch (line.substring(0, 1)) {
			case " ":
			case "+":
			case "-":
				currentDeltaCache.details.add(line);
				break;
			case "\\":
				break;
			default:
				if (line.startsWith("@@ ") || line.startsWith("diff --git")) {
					Chunk original = null;
					Chunk revised = null;
					switch (currentDeltaCache.level) {
						case ADD:
							revised = new Chunk(currentPatchCache.bPath, 
									currentDeltaCache.revisedPosition, currentDeltaCache.revisedRange,
									currentDeltaCache.details, Chunk.VERSION.REVISED);
							Delta insertDelta = new InsertDelta(original, revised, currentDeltaCache.details);
							diff.getLastPatch().addDelta(insertDelta);
							break;
						case SUB:
							original = new Chunk(currentPatchCache.aPath,
									currentDeltaCache.originalPosition, currentDeltaCache.originalRange,
									currentDeltaCache.details, Chunk.VERSION.ORIGINAL);
							Delta deleteDelta = new DeletaDelta(original, revised, currentDeltaCache.details);
							diff.getLastPatch().addDelta(deleteDelta);
							break;
						case MIX:
							original = new Chunk(currentPatchCache.aPath,
									currentDeltaCache.originalPosition, currentDeltaCache.originalRange,
									currentDeltaCache.details, Chunk.VERSION.ORIGINAL);
							revised = new Chunk(currentPatchCache.bPath, 
									currentDeltaCache.revisedPosition, currentDeltaCache.revisedRange,
									currentDeltaCache.details, Chunk.VERSION.REVISED);
							Delta modifyDelta = new ModifyDelta(original, revised, currentDeltaCache.details);
							diff.getLastPatch().addDelta(modifyDelta);
							break;
						default:
							throw new Exception("delta cache level has not been set");
					}
				} else {
					throw new Exception("ERROR in status: " + status.name()
							+ " unexpected start character of the line: " + line);
				}
				
				switch (line.substring(0, 2)) {
					case "@@":
						// set new delta cache
						Pattern pDelta = Pattern.compile("@@ -(.*) \\+(.*) @@.*");
						Matcher mDelta = pDelta.matcher(line);
						if (mDelta.find() && mDelta.groupCount() == 2) {							
							currentDeltaCache.reset();
							currentDeltaCache.level = DeltaCache.LEVEL.MIX;
							
							String originalMeta = mDelta.group(1);
							if (!originalMeta.contains(","))
								originalMeta = originalMeta + ",0";
							String[] originalNumbers = originalMeta.split(",");
							int originalPos = Integer.parseInt(originalNumbers[0]);
							currentDeltaCache.originalPosition = originalPos;
							int originalRng = Integer.parseInt(originalNumbers[1]);
							currentDeltaCache.originalRange = originalRng;
							
							String revisedMeta = mDelta.group(2);
							if (!revisedMeta.contains(","))
								revisedMeta = revisedMeta + ",0";
							String[] revisedNumbers = revisedMeta.split(",");
							int revisedPos = Integer.parseInt(revisedNumbers[0]);
							currentDeltaCache.revisedPosition = revisedPos;
							int revisedRng = Integer.parseInt(revisedNumbers[1]);
							currentDeltaCache.revisedRange = revisedRng;
							
							currentDeltaCache.details.add(line);
							
							status = STATUS.DELTA_HEADER_SET;
						} else {
							throw new Exception("in status " + status.name() + " a non-first delta header malformatted: " + line);
						}
						break;
					case "di":
						// clear delta cache
						currentDeltaCache.reset();
						// set new patch cache
						currentPatchCache.reset();
												
						Pattern pPatch = Pattern.compile("diff --git a/(.*) b/(.*)");
						Matcher mPatch = pPatch.matcher(line);
						if (mPatch.find() && mPatch.groupCount() == 2) {
							currentPatchCache.aPath = mPatch.group(1);
							currentPatchCache.bPath = mPatch.group(2);
							currentPatchCache.header.addHeaderLine(line);
							status = STATUS.PATCH_HEADER;
						} else {
							throw new Exception("in status " + status.name() + " a patch header first-line malformatted: " + line);
						}
						
						break;
					default:
						throw new Exception("Error in status: " + status.name() + " with unlikely case");
				}
				
				break;
		}
	}
	
	private void finalizeDiff(GitDiff diff, PatchCache currentPatchCache, DeltaCache currentDeltaCache) throws Exception {
		// after for loop
		Chunk original = null;
		Chunk revised = null;
		switch (currentDeltaCache.level) {
			case ADD:
				revised = new Chunk(currentPatchCache.bPath, 
						currentDeltaCache.revisedPosition, currentDeltaCache.revisedRange,
						currentDeltaCache.details, Chunk.VERSION.REVISED);
				Delta insertDelta = new InsertDelta(original, revised, currentDeltaCache.details);
				diff.getLastPatch().addDelta(insertDelta);
				break;
			case SUB:
				original = new Chunk(currentPatchCache.aPath,
						currentDeltaCache.originalPosition, currentDeltaCache.originalRange,
						currentDeltaCache.details, Chunk.VERSION.ORIGINAL);
				Delta deleteDelta = new DeletaDelta(original, revised, currentDeltaCache.details);
				diff.getLastPatch().addDelta(deleteDelta);
				break;
			case MIX:
				original = new Chunk(currentPatchCache.aPath,
						currentDeltaCache.originalPosition, currentDeltaCache.originalRange,
						currentDeltaCache.details, Chunk.VERSION.ORIGINAL);
				revised = new Chunk(currentPatchCache.bPath, 
						currentDeltaCache.revisedPosition, currentDeltaCache.revisedRange,
						currentDeltaCache.details, Chunk.VERSION.REVISED);
				Delta modifyDelta = new ModifyDelta(original, revised, currentDeltaCache.details);
				diff.getLastPatch().addDelta(modifyDelta);
				break;
			default:
				throw new Exception("delta cache level has not been set at the final step");
		}
		status = STATUS.READY;
	}

	// Helper method for getting the diff file content as list of strings
    private List<String> fileToLines(String diffFilePath) {
    	List<String> lines = new LinkedList<String>();
    	String line = "";
    	try {
    		BufferedReader input = new BufferedReader(new FileReader(diffFilePath));
    		while ((line = input.readLine()) != null)
    			lines.add(line);
    		input.close();
    	} catch (IOException e) {
    		e.printStackTrace();
    		System.exit(20);
    	}
    	return lines;
    }

	@Override
	public Map<String, Integer> oldPatchRange(GitDiff diff) {
		Map<String, Integer> output = new HashMap<String, Integer>();
		for (Patch patch : diff.getPatches()) {
			if (patch.getMode() != Patch.MODE.CREATE) {				
				String key = patch.getPreimagePath();
				int rangeSize = 0;
				for (Delta delta : patch.getDeltas()) {
					Chunk original = delta.getOriginal();
					rangeSize += original.getRange();
				}
				output.put(key, rangeSize);
			}
		}
		return output;
	}

	@Override
	public Map<String, Integer> newPatchRange(GitDiff diff) {
		Map<String, Integer> output = new HashMap<String, Integer>();
		for (Patch patch : diff.getPatches()) {
			if (patch.getMode() != Patch.MODE.REMOVE) {				
				String key = patch.getPostimagePath();
				int rangeSize = 0;
				for (Delta delta : patch.getDeltas()) {
					Chunk revised = delta.getRevised();
					rangeSize += revised.getRange();
				}
				output.put(key, rangeSize);
			}
		}
		return output;
	}

	@Override
	public Map<String, Integer[]> oldLinesRevised(GitDiff diff) {
		Map<String, Integer[]> output = new HashMap<String, Integer[]>();
		for (Patch patch : diff.getPatches()) {
			if (patch.getMode() != Patch.MODE.CREATE) {				
				String key = patch.getPreimagePath();
				List<Integer> lineNumbers = new ArrayList<Integer>();
				for (Delta delta : patch.getDeltas()) {
					if (delta.getType() != Delta.TYPE.INSERT) {
						Chunk original = delta.getOriginal();
						lineNumbers.addAll(original.getRevisedLineNumbers());
					}
				}
				Integer[] nums = new Integer[lineNumbers.size()];
				lineNumbers.toArray(nums);
				output.put(key, nums);
			}
		}
		return output;
	}

	@Override
	public Map<String, Integer[]> newLinesRevised(GitDiff diff) {
		Map<String, Integer[]> output = new HashMap<String, Integer[]>();
		for (Patch patch : diff.getPatches()) {
			if (patch.getMode() != Patch.MODE.REMOVE) {				
				String key = patch.getPostimagePath();
				List<Integer> lineNumbers = new ArrayList<Integer>();
				for (Delta delta : patch.getDeltas()) {
					if (delta.getType() != Delta.TYPE.DELETE) {
						Chunk revised = delta.getRevised();
						lineNumbers.addAll(revised.getRevisedLineNumbers());
					}
				}
				Integer[] nums = new Integer[lineNumbers.size()];
				lineNumbers.toArray(nums);
				output.put(key, nums);
			}
		}
		return output;
	}
	
	public static void main(String[] args) throws Exception {
		System.out.println("Git diff input processor -- test only");
		
		if (args.length > 0) {
			System.out.println("File path: " + args[0]);
			IInputProcessor processor = new InputDiffProcessor();
			GitDiff diff = processor.parseDiff(args[0]);
			Delta d1 = diff.getPatches().get(0).getDeltas().get(0);
			System.out.println(d1);
			if (d1.getType() != Delta.TYPE.INSERT)
				System.out.println("First patch's first delta's original chunk revised line numbers: "
						+ d1.getOriginal().getRevisedLineNumbers());
			Delta d2 = diff.getLastPatch().getDeltas().get(0);
			System.out.println(d2);
			if (d2.getType() != Delta.TYPE.DELETE) {
				Chunk revisedChunk = d2.getRevised();
				System.out.println("Last patch's first delta's revised chunk's first revised line: \n"
						+ revisedChunk.getLineByLineNumber(revisedChunk.getRevisedLineNumbers().get(0)));
			}
		}
	}
	
}
