package edu.ucsd.getty.visitors;

import static org.junit.Assert.*;

import java.io.FileInputStream;

import org.junit.Test;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;

import edu.ucsd.getty.visitors.MethodDeclarationSrcVisitor;


public class MethodVisitorTest {

	@Test
	public void testVisitor() {
		try {
			// creates an input stream for the file to be parsed
	        FileInputStream in = new FileInputStream(
	        		"test/data/src/TestJavaSource.java.file");
            // parse the file
            CompilationUnit cu = JavaParser.parse(in);
			in.close();
			
			MethodDeclarationSrcVisitor visitor = new MethodDeclarationSrcVisitor();
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

}
