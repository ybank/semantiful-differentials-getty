package edu.ucsd.getty.diff.caches;

import java.util.List;
import java.util.ArrayList;

public class DeltaCache {

	public List<String> details = new ArrayList<String>();
	// set at DELTA_UNIT/DELTA_HAEDER_SET/DELTA_BODY
	
	public int originalPosition = 0;
	// set at DELTA_UNIT/DELTA_BODY
	
	public int originalRange = 0;
	// set at DELTA_UNIT/DELTA_BODY
	
	public int revisedPosition = 0;
	// set at DELTA_UNIT/DELTA_BODY
	
	public int revisedRange = 0;
	// set at DELTA_UNIT/DELTA_BODY

	public static enum LEVEL {
		DEFAULT, ADD, SUB, MIX;
	}
	
	public LEVEL level = LEVEL.DEFAULT;
	// set at DELTA_UNIT/DELTA_BODY
	
	public void reset() {
		this.originalPosition = 0;
		this.originalRange = 0;
		this.revisedPosition = 0;
		this.revisedRange = 0;
		this.details = new ArrayList<String>();
		this.level = LEVEL.DEFAULT;
	}
	
}
