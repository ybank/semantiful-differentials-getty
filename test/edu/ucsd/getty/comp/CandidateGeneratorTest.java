package edu.ucsd.getty.comp;

import static org.junit.Assert.*;

import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Test;

public class CandidateGeneratorTest {

	@Test
	public void testTraceGeneratorSingleMethod() {
		Set<String> dummy = new HashSet<String>();
		CandidateGenerator generator = new CandidateGenerator(
				dummy, "test/data/lib/test_email.jar");
		Set<List<String>> possible_traces = generator.getCandidateTraces(
				"org.apache.commons.mail.ImageHtmlEmail:replacePattern");
		List<String> one_expected = new LinkedList<String>();
		one_expected.add("org.apache.commons.mail.ImageHtmlEmail:replacePattern");
		one_expected.add("org.apache.commons.mail.ImageHtmlEmail:buildMimeMessage");
		one_expected.add("org.apache.commons.mail.Email:send");
		assert possible_traces.contains(one_expected);
	}
	
	@Test
	public void testTraceGeneratorMultipleMethods() {
		Set<String> methods = new HashSet<String>();
		String method1 = "org.apache.commons.math3.primes.SmallPrimes:trialDivision";
		String method2 = "org.apache.commons.math3.analysis.UnivariateVectorFunction:value";
		String method3 = "org.apache.commons.math3.geometry.partitioning.BoundaryProjector:getProjection";
		methods.add(method1);
		methods.add(method2);
		methods.add(method3);
		String pkg = "org.apache.commons.math3";
		CandidateGenerator generator = new CandidateGenerator(methods, "test/data/lib/test_maths.jar", pkg);
		Map<String, Set<List<String>>> candidate_map = generator.getCandidateTraces();
		assertEquals(1, candidate_map.get(method1).size());
		List<String> temp = null;
		for (List<String> element : candidate_map.get(method1))
			temp = element;
		assertEquals(2, temp.size());
		assertEquals(1, candidate_map.get(method2).size());
		assert candidate_map.get(method3).size() > 2000;
	}
	
}
