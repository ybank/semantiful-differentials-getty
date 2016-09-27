package edu.ucsd.getty.visitors;

import static org.junit.Assert.*;

import java.io.FileInputStream;
import java.util.HashMap;
import java.util.Map;

import org.junit.Test;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;

import edu.ucsd.getty.visitors.MethodLineNumberSrcVisitor;


public class MethodVisitorTest {

	@Test
	public void testLineNumberVisitor() {
		try {
			// creates an input stream for the file to be parsed
	        FileInputStream in = new FileInputStream(
	        		"java/test/data/src/TestJavaSource.java.file");
            // parse the file
            CompilationUnit cu = JavaParser.parse(in);
			in.close();
			
			MethodLineNumberSrcVisitor visitor = new MethodLineNumberSrcVisitor();
			MethodDeclaration decl = (MethodDeclaration) visitor.visit(cu, new Integer(39));
			
//			System.out.println(decl.toString());
			assertEquals("class com.github.javaparser.ast.body.MethodDeclaration", 
					decl.getClass().toString());
			
			assertEquals(36, decl.getBeginLine());
			assertEquals(42, decl.getEndLine());
			assertEquals("innerMethod", decl.getName());
			
//			System.out.println(decl.getParentNode().toString());
			
			assertEquals("class com.github.javaparser.ast.body.ClassOrInterfaceDeclaration", 
					decl.getParentNode().getClass().toString());
			assertEquals("ReadMeIn", ((ClassOrInterfaceDeclaration) decl.getParentNode()).getName());
			
			assertEquals("com.github.javaparser.ast.body.ClassOrInterfaceDeclaration",
					decl.getParentNode().getClass().getName());
			assertTrue(decl.getParentNode() instanceof ClassOrInterfaceDeclaration);
			
			assertEquals("class com.github.javaparser.ast.body.ClassOrInterfaceDeclaration", 
					decl.getParentNode().getParentNode().getClass().toString());
			assertEquals("TestJavaSource",
					((ClassOrInterfaceDeclaration) decl.getParentNode().getParentNode()).getName());
			
			assertEquals("class com.github.javaparser.ast.CompilationUnit", 
					decl.getParentNode().getParentNode().getParentNode().getClass().toString());
			assertEquals("some.pack",
					((CompilationUnit) decl.getParentNode().getParentNode().getParentNode())
					.getPackage().getName().toString());
			
		} catch (Exception e) {
			e.printStackTrace();
			fail("tests are not performed properly");
		}
	}
	
	@Test
	public void testClassDeclarationVisitor() {
		try {
			// creates an input stream for the file to be parsed
	        FileInputStream in = new FileInputStream(
	        		"java/test/data/src/RealClassTest.java.file");
            // parse the file
            CompilationUnit cu = JavaParser.parse(in);
			in.close();
			
			Map<String, Integer> results = new HashMap<String, Integer>();
			
			MethodDeclarationVisitor visitor = new MethodDeclarationVisitor();
			visitor.visit(cu, results);
			
			assertEquals(19, results.keySet().size());
			assertEquals(48, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:<init>"));
			assertEquals(64, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:get"));
			assertEquals(93, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:reset"));
			assertEquals(98, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:add"));
			assertEquals(142, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:hashCode"));
			assertEquals(191, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Factory:newInstance"));
			assertEquals(209, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Map:<init>"));
			assertEquals(214, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Map:getCounts"));
			assertEquals(224, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Map:sum"));
			
		} catch (Exception e) {
			e.printStackTrace();
			fail("tests are not performed properly");
		}
	}
	
	@Test
	public void testEnumDeclarationVisitor() {
		try {
			// creates an input stream for the file to be parsed
	        FileInputStream in = new FileInputStream(
	        		"java/test/data/src/RealEnumTest.java.file");
            // parse the file
            CompilationUnit cu = JavaParser.parse(in);
			in.close();
			
			Map<String, Integer> results = new HashMap<String, Integer>();
			
			MethodDeclarationVisitor visitor = new MethodDeclarationVisitor();
			visitor.visit(cu, results);
			
			assertEquals(3, results.keySet().size());
			assertEquals(15, (int) results.get("com.crunchify.tutorials.CrunchifyEnumExample:<init>"));
			assertEquals(19, (int) results.get("com.crunchify.tutorials.CrunchifyEnumExample:companyDetails"));
			assertEquals(40, (int) results.get("com.crunchify.tutorials.CrunchifyEnumExample:main"));
			
		} catch (Exception e) {
			e.printStackTrace();
			fail("tests are not performed properly");
		}
	}

}
