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
			
			assertEquals(25, results.keySet().size());
			assertEquals(48, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:<init>-48"));
			assertEquals(64, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:get-64"));
			assertEquals(93, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:reset-93"));
			assertEquals(98, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:add-98"));
			assertEquals(142, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters:hashCode-142"));
			assertEquals(191, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Factory:newInstance-191"));
			assertEquals(209, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Map:<init>-209"));
			assertEquals(214, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Map:getCounts-214"));
			assertEquals(224, (int) results.get("org.apache.hadoop.hdfs.util.EnumCounters$Map:sum-224"));
			
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
			assertEquals(15, (int) results.get("com.crunchify.tutorials.CrunchifyEnumExample:<init>-15"));
			assertEquals(19, (int) results.get("com.crunchify.tutorials.CrunchifyEnumExample:companyDetails-19"));
			assertEquals(40, (int) results.get("com.crunchify.tutorials.CrunchifyEnumExample:main-40"));
			
		} catch (Exception e) {
			e.printStackTrace();
			fail("tests are not performed properly");
		}
	}

}
