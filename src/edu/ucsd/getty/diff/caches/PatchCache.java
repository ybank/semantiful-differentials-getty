package edu.ucsd.getty.diff.caches;

import java.util.ArrayList;

import edu.ucsd.getty.diff.Patch;

public class PatchCache {
	
	public String aPath = null;
	// set at READY, modified and finalized at PATCH_HEADER
	
	public String bPath = null;
	// set at READY, modified and finalized at HEADER_COMPLETION
	
	public Patch.Header header = new Patch.Header(new ArrayList<String>());
	// set at READY, PATCH_HEADER, HEADER_COMPLETION
	
	public static enum LEVEL {
		DEFAULT, CRE, REM, UPD;
	}
	
	public LEVEL level = LEVEL.DEFAULT;
	// set at PATCH_HEADER, HEADER_COMPLETION
	
	public void reset() {
		this.aPath = null;
		this.bPath = null;
		this.header = new Patch.Header(new ArrayList<String>());
		this.level = LEVEL.DEFAULT;
	}

}
