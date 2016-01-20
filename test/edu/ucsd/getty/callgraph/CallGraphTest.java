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

}
