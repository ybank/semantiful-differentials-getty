package edu.ucsd.getty.diff;

public class CreatePatch extends Patch {

	public CreatePatch(String aPath, String bPath, Header header) {
		super(aPath, bPath, header);
	}

	@Override
	public MODE getMode() {
		return MODE.CREATE;
	}

}
