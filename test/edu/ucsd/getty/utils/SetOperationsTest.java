package edu.ucsd.getty.utils;

import java.util.HashSet;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

public class SetOperationsTest {
	
	private Set<String> abc;
	private Set<String> abc2;
	private Set<String> def;
	private Set<String> efg;
	private Set<String> fgh;

	@Before
	public void setUp() throws Exception {
		abc = new HashSet<String>();
		abc.add("aaa");
		abc.add("bbb");
		abc.add("ccc");
		
		abc2 = new HashSet<String>();
		abc2.add("aaa");
		abc2.add("bbb");
		abc2.add("ccc");
		
		def = new HashSet<String>();
		def.add("ddd");
		def.add("eee");
		def.add("fff");
		
		efg = new HashSet<String>();
		efg.add("eee");
		efg.add("fff");
		efg.add("ggg");
		
		fgh = new HashSet<String>();
		fgh.add("fff");
		fgh.add("ggg");
		fgh.add("hhh");
	}

	@Test
	public void testIntersection() {
		Set<String> expected1 = new HashSet<String>();
		expected1.add("aaa");
		expected1.add("bbb");
		expected1.add("ccc");
		assert expected1.equals(SetOperations.intersection(abc, abc2));
		
		Set<String> expected2 = new HashSet<String>();
		expected2.add("ddd");
		expected2.add("eee");
		assert expected2.equals(SetOperations.intersection(def, efg));
		
		Set<String> expected3 = new HashSet<String>();
		assert expected3.equals(SetOperations.intersection(def, abc));
	}

	@Test
	public void testUnion() {
		Set<String> expected1 = new HashSet<String>();
		expected1.add("aaa");
		expected1.add("bbb");
		expected1.add("ccc");
		assert expected1.equals(SetOperations.union(abc, abc2));
		
		Set<String> expected2 = new HashSet<String>();
		expected2.add("ddd");
		expected2.add("eee");
		expected2.add("fff");
		expected2.add("ggg");
		expected2.add("hhh");
		assert expected2.equals(SetOperations.union(def, fgh));
	}

	@Test
	public void testDifference() {
		Set<String> expected1 = new HashSet<String>();
		assert expected1.equals(SetOperations.difference(abc, abc2));
		
		assert abc.equals(SetOperations.difference(abc, def));
		
		Set<String> expected2 = new HashSet<String>();
		expected2.add("ddd");
		assert expected2.equals(SetOperations.difference(def, efg));
	}

	@Test
	public void testSymmetric_difference() {
		Set<String> expected1 = new HashSet<String>();
		assert expected1.equals(SetOperations.symmetric_difference(abc, abc2));
		
		Set<String> expected2 = new HashSet<String>();
		expected2.add("aaa");
		expected2.add("bbb");
		expected1.add("ccc");
		expected2.add("ddd");
		expected2.add("eee");
		expected1.add("fff");
		assert expected1.equals(SetOperations.symmetric_difference(abc, def));
		
		Set<String> expected3 = new HashSet<String>();
		expected3.add("ddd");
		expected3.add("eee");
		expected3.add("ggg");
		expected3.add("hhh");
		assert expected1.equals(SetOperations.symmetric_difference(def, fgh));
	}

}
