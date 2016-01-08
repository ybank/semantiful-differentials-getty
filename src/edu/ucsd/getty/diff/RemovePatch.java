package edu.ucsd.getty.diff;

public class RemovePatch extends Patch {

	public RemovePatch(String aPath, String bPath, Header header) {
		super(aPath, bPath, header);
	}

	@Override
	public MODE getMode() {
		return MODE.REMOVE;
	}

}
