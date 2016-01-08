package edu.ucsd.getty.diff;

public class UpdatePatch extends Patch {

	public UpdatePatch(String aPath, String bPath, Header header) {
		super(aPath, bPath, header);
	}

	@Override
	public MODE getMode() {
		return MODE.UPDATE;
	}

}
