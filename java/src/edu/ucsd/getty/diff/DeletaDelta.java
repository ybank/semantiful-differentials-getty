package edu.ucsd.getty.diff;

import java.util.List;

public class DeletaDelta extends Delta {

	public DeletaDelta(Chunk original, Chunk revised, List<String> details) {
		super(original, revised, details);
	}

	@Override
	public TYPE getType() {
		return TYPE.DELETE;
	}

}
