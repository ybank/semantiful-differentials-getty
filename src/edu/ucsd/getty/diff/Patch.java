package edu.ucsd.getty.diff;

import java.util.ArrayList;
import java.util.List;

public abstract class Patch {
	
	private final String preimagePath;
	private final String postimagePath;
	private List<Delta> deltas;
	
	// TODO actual header content
	public static class Header {
		private List<String> headerLines;
		
		public Header(List<String> lines) {
			this.headerLines = lines;
		}
		
		public List<String> getLines() {
			return this.headerLines;
		}
		
		public boolean addHeaderLine(String line) {
			return this.headerLines.add(line);
		}
		
		public void completion() {
			// TODO if there is a need to set rich header info
			// this requires going over all lines again
		}
	}
	
	private final Header header;
	
	public static enum MODE {
		CREATE, REMOVE, UPDATE
	}
	
	public abstract MODE getMode();
	
	public Patch(String aPath, String bPath, Header header) {
		this.preimagePath = aPath;
		this.postimagePath = bPath;
		this.deltas = new ArrayList<Delta>();
		this.header = header;
	}
	
	public Header getHeader() {
		return header;
	}

	public List<Delta> getDeltas() {
		return this.deltas;
	}
	
	public void addDelta(Delta delta) {
		this.deltas.add(delta);
	}
	
	public void addDeltas(List<Delta> deltas) {
		this.deltas.addAll(deltas);
	}
	
	public String getPreimagePath() {
		return this.preimagePath;
	}
	
	public String getPostimagePath() {
		return this.postimagePath;
	}
	
}
