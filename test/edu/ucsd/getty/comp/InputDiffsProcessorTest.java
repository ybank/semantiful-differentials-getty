package edu.ucsd.getty.comp;

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.Test;

import edu.ucsd.getty.IInputProcessor;
import edu.ucsd.getty.comp.InputDiffProcessor;
import edu.ucsd.getty.diff.Chunk;
import edu.ucsd.getty.diff.Delta;
import edu.ucsd.getty.diff.GitDiff;
import edu.ucsd.getty.diff.Patch;

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
			
			assertEquals(4, diff.getPatches().size());
			
			Patch p1 = diff.getPatches().get(0);
			assertEquals(Patch.MODE.CREATE, p1.getMode());
			assertEquals(1, p1.getDeltas().size());
			assertEquals(null, p1.getDeltas().get(0).getOriginal());
			assertEquals(Chunk.VERSION.REVISED, p1.getDeltas().get(0).getRevised().version);
			
			Patch p2 = diff.getPatches().get(1);
			assertEquals(Patch.MODE.REMOVE, p2.getMode());
			assertEquals(1, p2.getDeltas().size());
			assertEquals(Delta.TYPE.DELETE, p2.getDeltas().get(0).getType());
			
			Patch p3 = diff.getPatches().get(2);
			assertEquals(3, p3.getDeltas().size());
			Delta d32 = p3.getDeltas().get(1);
			Chunk original = d32.getOriginal();
			Chunk revised = d32.getRevised();
			rangeTest(44, 10, original);
			rangeTest(43, 13, revised);
			List<Integer> expectedLineNumbersOriginal = new ArrayList<Integer>();
			expectedLineNumbersOriginal.add(50);
			lineNumberTest(expectedLineNumbersOriginal, original);
			Integer[] revisedLineNumbers = new Integer[] {46, 47, 51, 52};
			List<Integer> expectedLineNumbersRevised = new ArrayList<Integer>(
					Arrays.asList(revisedLineNumbers));
			lineNumberTest(expectedLineNumbersRevised, revised);
			
			Patch p4 = diff.getLastPatch();
			assertEquals(1, p4.getDeltas().size());
			Delta d4 = p4.getDeltas().get(0);
			assertEquals(9, d4.getDetails().size());
			revisedLineTest("\t{", d4.getRevised(), 55);
			revisedLineTestByOffset("\t", d4.getRevised(), 6);
			assertEquals(8, d4.getRevised().getLines().size());
			
			// test 4 methods in the processor
			Map<String, Integer> oldRange = processor.oldPatchRange(diff);
			Map<String, Integer> oldRangeExpected = new HashMap<String, Integer>();
			oldRangeExpected.put("DeleteDelta.java.file", 82);
			oldRangeExpected.put("ModifyDelta.java.file", 30);
			oldRangeExpected.put("TestJavaSource2.java.file", 4);
			assertEquals(oldRangeExpected, oldRange);
			
			Map<String, Integer> newRange = processor.newPatchRange(diff);
			assertEquals(36, newRange.get("ModifyDelta.java.file").intValue());
			
			Map<String, Integer[]> oldLines = processor.oldLinesRevised(diff);
			Integer[] expectedOldLines = new Integer[] {
					2, 50, 84, 85, 86, 87, 88, 89
			};
			assertArrayEquals(expectedOldLines, oldLines.get("ModifyDelta.java.file"));
			
			Map<String, Integer[]> newLines = processor.newLinesRevised(diff);
			Integer[] expectedNewLines = new Integer[] {
					46, 47, 51, 52, 91, 92, 93, 94, 95, 96, 97, 99, 100, 101
			};
			assertArrayEquals(expectedNewLines, newLines.get("ModifyDelta.java.file"));
			
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	private void rangeTest(int expectedPos, int expectedRng, Chunk chunk) {
		assertEquals(expectedPos, chunk.getPosition());
		assertEquals(expectedRng, chunk.getRange());
		List<Integer> rangeNumbers = chunk.getRangeLineNumbers();
		assertEquals(expectedPos, rangeNumbers.get(0).intValue());
		assertEquals(expectedPos + expectedRng - 1, 
				rangeNumbers.get(rangeNumbers.size() - 1).intValue());
	}
	
	private void lineNumberTest(List<Integer> expectedLinenumbers, Chunk chunk) {
		List<Integer> actualLineNumbers = chunk.getRevisedLineNumbers();
		assertEquals(expectedLinenumbers, actualLineNumbers);
	}
	
	private void revisedLineTest(String expectedLine, Chunk chunk, int number) {
		String actualLine = chunk.getLineByLineNumber(number);
		assert expectedLine.equals(actualLine);
	}
	
	private void revisedLineTestByOffset(String expectedLine, Chunk chunk, int offset) {
		String actualLine = chunk.getLineByOffset(offset);
		assert expectedLine.equals(actualLine);
	}

}
