package edu.ucsd.getty.utils;

import static org.junit.Assert.*;

import java.util.Set;

import org.junit.Test;

public class DataStructureBuilderTest {

	@Test
	public void testLoadSetFrom() {
		String path = "test/data/ex/set.ex";
		Set<String> methods = DataStructureBuilder.loadSetFrom(path);
		assertEquals(35, methods.size());
		assert methods.contains("org.apache.commons.bcel6.verifier.statics.Pass3aVerifier:verify");
		assert methods.contains("org.apache.commons.bcel6.generic.Select:<init>");
		assert !methods.contains("");
	}

}
