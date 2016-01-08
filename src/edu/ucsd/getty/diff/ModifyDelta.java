package edu.ucsd.getty.diff;

import java.util.List;

public class ModifyDelta extends Delta {

	public ModifyDelta(Chunk original, Chunk revised, List<String> details) {
		super(original, revised, details);
	}

	@Override
	public TYPE getType() {
		return TYPE.MODIFY;
	}

}
