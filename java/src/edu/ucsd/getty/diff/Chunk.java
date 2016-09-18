package edu.ucsd.getty.diff;

import java.util.ArrayList;
import java.util.List;

public class Chunk {
	
	private final String filePath;

	private final int position;
	private final int range;
	
	public static enum VERSION {
		UNCLEAR, ORIGINAL, REVISED;
	}
	public VERSION version;
	
	// the actual lines in this image
	private List<String> lines;
	
	// only the actual line numbers where changes took place
	private List<Integer> revisedLineNumbers;
	
	public Chunk(String path, int pos, int rng) {
		this.filePath = path;
		this.position = pos;
		this.range = rng;
		this.lines = new ArrayList<String>();
		this.revisedLineNumbers = new ArrayList<Integer>();
		this.version = VERSION.UNCLEAR;
	}
	
	public Chunk(String path, int pos, int rng, List<String> deltaLines, VERSION vsn) throws Exception {
		this.filePath = path;
		this.position = pos;
		this.range = rng;
		this.lines = new ArrayList<String>();
		this.revisedLineNumbers = new ArrayList<Integer>();
		this.version = vsn;
		switch (this.version) {
			case ORIGINAL:
				int offset4original = 0;
				for (String deltaLine : deltaLines) {
					switch (deltaLine.substring(0, 1)) {
						case " ":
							this.lines.add(deltaLine.substring(1));
							offset4original ++;
							break;
						case "-":
							this.lines.add(deltaLine.substring(1));
							this.revisedLineNumbers.add(this.position + offset4original);
							offset4original ++;
							break;
						case "+":
						case "\\":
						case "@":
							break;
						default:
							throw new Exception("original chunk creation unable to handle this line: " + deltaLine);
					}
				}
				break;
			case REVISED:
				int offset4revised = 0;
				for (String deltaLine : deltaLines) {
					switch (deltaLine.substring(0, 1)) {
						case " ":
							this.lines.add(deltaLine.substring(1));
							offset4revised ++;
							break;
						case "+":
							this.lines.add(deltaLine.substring(1));
							this.revisedLineNumbers.add(this.position + offset4revised);
							offset4revised ++;
							break;
						case "-":
						case "\\":
						case "@":
							break;
						default:
							throw new Exception("revised chunk creation unable to handle this line: " + deltaLine);
					}
				}
				break;
			default:
				throw new Exception("incorrect chunk version");
		}
	}

	public int getPosition() {
		return this.position;
	}

	public int getRange() {
		return this.range;
	}
	
	public List<String> getLines() {
		return this.lines;
	}
	
	public boolean setLines(List<String> actualLines) {
		return this.lines.addAll(actualLines);
	}
	
	public boolean addLine(String aLine) {
		return this.lines.add(aLine);
	}
	
	public List<Integer> getRevisedLineNumbers() {
		return this.revisedLineNumbers;
	}
	
	public boolean setRevisedLineNumbers(List<Integer> numbers) {
		return this.revisedLineNumbers.addAll(numbers);
	}
	
	public boolean addRevisedLineNumber(int number) {
		return this.revisedLineNumbers.add(number);
	}
	
	public boolean isValid() {
		return this.range >= this.lines.size()
				&& this.lines.size() >= this.revisedLineNumbers.size();
	}
	
	public List<Integer> getRangeLineNumbers() {
		List<Integer> lineNumbers = new ArrayList<Integer>();
		for (int i = 0; i < this.range; i++) {
			lineNumbers.add(this.position + i);
		}
		return lineNumbers;
	}
	
	public String getLineByOffset(int offset) {
		// offset index start from 0
		if (offset >= range || offset >= lines.size())
			throw new IndexOutOfBoundsException("offset out of bounds: " + offset +
					" valid range: 0 - " + range + " (or " + (lines.size() - 1) + ")");
		else {
			return this.lines.get(offset);
		}
	}
	
	public String getLineByLineNumber(int lineNumber) {
		if (lineNumber < position || lineNumber >= position + range)
			throw new IndexOutOfBoundsException("line number out of bounds: " + lineNumber +
					" valid line number range: " + position + " - " + (position + range - 1));
		else {
			return this.lines.get(lineNumber - position);
		}
	}
	
	public String getFilePath() {
		return filePath;
	}
}
