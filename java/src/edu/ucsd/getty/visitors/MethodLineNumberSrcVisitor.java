package edu.ucsd.getty.visitors;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.GenericVisitorAdapter;

public class MethodLineNumberSrcVisitor extends GenericVisitorAdapter<Node, Integer> {

	public Node visit(final MethodDeclaration n, final Integer arg) {
		int lineNumber = arg.intValue();
		if (n.getBeginLine() <= lineNumber && n.getEndLine() >= lineNumber) {
			return n;
		}
		return null;
	}
	
	public Node visit(final ConstructorDeclaration n, final Integer arg) {
		int lineNumber = arg.intValue();
		if (n.getBeginLine() <= lineNumber && n.getEndLine() >= lineNumber) {
			return n;
		}
		return null;
	}

}
