package edu.ucsd.getty.comp;

import static org.junit.Assert.assertEquals;

import java.io.FileInputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;

import edu.ucsd.getty.IMethodRecognizer;
import edu.ucsd.getty.visitors.MethodDeclarationSrcVisitor;

public class ASTInspector implements IMethodRecognizer {

	@Override
	public Set<String> changedMethods(String targetFolder, Map<String, Integer[]> diffs) {
		// TODO Auto-generated method stub
		return null;
	}
	
	@Override
	public Set<String> changedMethods(Map<String, Integer[]> diffs) {
		// each diff is a pair of source file and its list of line numbers changed
		Set<String> allChanged = new HashSet<String>();
		for (String source : diffs.keySet()) {
			try {
				FileInputStream in = new FileInputStream(source);
				CompilationUnit cu = JavaParser.parse(in);
				in.close();
				
				Integer[] lines = diffs.get(source);
				for (int line : lines) {
					String possibleMethod = this.changedMethod(cu, line);
					if (possibleMethod != null)
						allChanged.add(possibleMethod);
				}
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
		return allChanged;
	}
	
	protected String changedMethod(CompilationUnit cu, int lineNumber) {
		try {
			String qualifiedMethodName = null;
			
			MethodDeclarationSrcVisitor visitor = new MethodDeclarationSrcVisitor();
			Node visited = visitor.visit(cu, lineNumber);
			if (visited == null)
				return null;
			MethodDeclaration decl = (MethodDeclaration) visited;
			
			qualifiedMethodName = this.getQualifiedName(decl);
			
			return qualifiedMethodName;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	
	private String getQualifiedName(MethodDeclaration decl) throws Exception {
		String methodName = decl.getName();
		Node parent = decl.getParentNode();
		while (parent != null) {
			String className = parent.getClass().getName();
			if (className.equals("com.github.javaparser.ast.body.ClassOrInterfaceDeclaration"))
				methodName = ((ClassOrInterfaceDeclaration) parent).getName() + "." + methodName;
			else if (className.equals("com.github.javaparser.ast.CompilationUnit"))
				methodName = ((CompilationUnit) parent).getPackage().getName().toString() + "." + methodName;
			else
				// throw new Exception("unprocessed type: " + className);
				System.out.println("unprocessed type: " + className);
			parent = parent.getParentNode();
		}
		return methodName;
	}

	public static void main(String[] args) {
		System.out.println("Inspector of method name by AST");
		
//		IMethodRecognizer rec = new ASTInspector();
//		Map<String, Integer[]> diffs = new HashMap<String, Integer[]>();
//		diffs.put("/Users/yanyan/Projects/studies/implementation_alt/commons-math/src/main/java/org/apache/commons/math3/analysis/function/Gaussian.java", new Integer[]{155});
//		Set<String> result = rec.changedMethods(diffs);
//		for (String k : result)
//			System.out.println(k);
//		
//		IMethodRecognizer rec2 = new ASTInspector();
//		Map<String, Integer[]> diffs2 = new HashMap<String, Integer[]>();
//		diffs2.put("/Users/yanyan/Projects/studies/implementation_alt/commons-math/src/main/java/org/apache/commons/math3/analysis/differentiation/SparseGradient.java", new Integer[]{300});
//		Set<String> result2 = rec.changedMethods(diffs2);
//		for (String k : result2)
//			System.out.println(k);
	}

}
