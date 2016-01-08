package edu.ucsd.getty.comp;

import static org.junit.Assert.*;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.Test;

import edu.ucsd.getty.IInputProcessor;
import edu.ucsd.getty.comp.InputDiffProcessor;
import edu.ucsd.getty.diff.GitDiff;

public class InputDiffsProcessorTest {

	/** 
	 * some data for test:
	 *   preimagge commit: 2c1d7c0
	 *   postimage commit: da95ef6
	 *   src: test/data/src/*.file
	 *   diff: test/data/diff/test.diff
	 */
	
	@Test
	public void testParseDiff() {
		IInputProcessor processor = new InputDiffProcessor();
		try {
			GitDiff diff = processor.parseDiff("test/data/diff/test.diff");
			
			fail("not tested");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
