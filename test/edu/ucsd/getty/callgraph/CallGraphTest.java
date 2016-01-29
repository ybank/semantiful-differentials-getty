package edu.ucsd.getty.callgraph;

import java.util.Set;

import org.junit.Test;

public class CallGraphTest {

	@Test
	public void testCallGraphGenerationFromJar() {
		CallGraphAnalyzer analyzer = new CallGraphAnalyzer("org.apache.commons.email");
		CallGraph callgraph = analyzer.analyze(
				"test/data/lib/test_email.jar");
		Set<String> possible = callgraph.getPossibleCallersOf(
				"org.apache.commons.mail.resolver.DataSourceFileResolver:resolve");
		String one = "org.apache.commons.mail.ImageHtmlEmail:replacePattern";
		assert possible.contains(one);
	}
	
	@Test
	public void testCallGraphGenerationFromClasses() {
		CallGraphAnalyzer analyzer = new CallGraphAnalyzer("org.apache.commons.email");
		CallGraph callgraph = analyzer.analyze(
				"test/data/bin");
		Set<String> possible = callgraph.getPossibleCallersOf(
				"org.apache.commons.mail.resolver.DataSourceFileResolver:resolve");
		String one = "org.apache.commons.mail.ImageHtmlEmail:replacePattern";
		assert possible.contains(one);
	}
	
	@Test
	public void testCallGraphPossibleCallers() {
		CallGraphAnalyzer analyzer = new CallGraphAnalyzer("org.apache.commons.math3");
		CallGraph callgraph = analyzer.analyze(
				"test/data/lib/test_maths.jar");
		Set<String> staticCallers = callgraph.getStaticCallersOf(
				"org.apache.commons.math3.geometry.euclidean.threed.Line:toSpace");
		Set<String> possibleCallers = callgraph.getPossibleCallersOf(
				"org.apache.commons.math3.geometry.euclidean.threed.Line:toSpace");
		String one = "org.apache.commons.math3.geometry.partitioning.BoundaryProjector:singularProjection";
		assert !staticCallers.contains(one);
		assert possibleCallers.contains(one);
	}
	
	@Test
	public void test_test() {
		String empty = "[]";
		String[] e = empty.substring(1, empty.length()-1).split(", ");
		System.out.println(e.length);
		System.out.println(e[0]);
		
		String one = "[\"first.class:method\", ]";
		String[] o = one.substring(1, one.length()-1).split(", ");
		System.out.println(o.length);
		System.out.println(o[0]);
		
		String many = "[\"first.class:method\", \"second.class$inner:method\", \"third.class:method\", ]";
		String[] m = many.substring(1, many.length()-1).split(", ");
		System.out.println(m.length);
		System.out.println(m[0]);
		System.out.println(m[1]);
		System.out.println(m[2]);
	}

}
