package edu.ucsd.getty.diff;

import java.util.List;

public class InsertDelta extends Delta {

	public InsertDelta(Chunk original, Chunk revised, List<String> details) {
		super(original, revised, details);
	}

	@Override
	public TYPE getType() {
		return TYPE.INSERT;
	}

}
