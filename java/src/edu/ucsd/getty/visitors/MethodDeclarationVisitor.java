package edu.ucsd.getty.visitors;

import java.util.Map;

import com.github.javaparser.ast.body.BodyDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.TypeDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import edu.ucsd.getty.comp.ASTInspector;

public class MethodDeclarationVisitor extends VoidVisitorAdapter<Map<String, Integer>> {

	public void visit(
			final ClassOrInterfaceDeclaration decl, Map<String, Integer> targets_map) {
		set_for_all_methods(decl, targets_map);
	}

	public void visit(
			final EnumDeclaration decl, Map<String, Integer> targets_map) {
		set_for_all_methods(decl, targets_map);
	}
	
	private void set_for_all_methods(
			final TypeDeclaration decl, Map<String, Integer> targets_map) {
		try {
//			System.out.println("<getty> processing members list of " + decl.getName() + " ...");
			for (BodyDeclaration bd : decl.getMembers()) {
				if (bd instanceof MethodDeclaration) {
					String method_name = 
							ASTInspector.getQualifiedMethodName((MethodDeclaration) bd);
					int begin_line = bd.getBeginLine();
					if (targets_map.containsKey(method_name)) {
						int existed_ln = targets_map.get(method_name);
						if (existed_ln > begin_line)
							targets_map.put(method_name, begin_line);
					} else {
						targets_map.put(method_name, begin_line);
					}
				} else if (bd instanceof ConstructorDeclaration) {
					String constructor_name = 
							ASTInspector.getQualifiedConstructorName((ConstructorDeclaration) bd);
					int begin_line = bd.getBeginLine();
					if (targets_map.containsKey(constructor_name)) {
						int existed_ln = targets_map.get(constructor_name);
						if (existed_ln > begin_line)
							targets_map.put(constructor_name, begin_line);
					} else {
						targets_map.put(constructor_name, begin_line);
					}
				} else if (bd instanceof ClassOrInterfaceDeclaration) {
					visit((ClassOrInterfaceDeclaration) bd, targets_map);
				} else if (bd instanceof EnumDeclaration) {
					visit((EnumDeclaration) bd, targets_map);
				}
			}
		} catch (Exception e) {
			System.out.println("<getty> unable to process declaration: " + decl.getName() + 
					" between lines: " + decl.getBeginLine() + " and " + decl.getEndLine());
		}
	}

}
