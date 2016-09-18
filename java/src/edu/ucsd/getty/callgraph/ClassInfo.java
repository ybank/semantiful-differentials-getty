package edu.ucsd.getty.callgraph;

import java.util.HashSet;
import java.util.Set;

import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.classfile.Method;

public class ClassInfo {

	private final JavaClass self;
	
	// will be set once when it is initialized
	public final String qualifiedName; 
	public final String packageName;
	
	// will be set when it is initialized, then updated in analyzer, twice
	public Set<String> methods;
	
	// will be set more in analyzer
	public Set<String> supers;  // super class (maybe more for interface) and iterfaces
	public Set<String> subs;  // sub classes or implementations
	
	public ClassInfo(JavaClass self) {
		this.self = self;
		
		this.qualifiedName = self.getClassName();
		this.packageName = self.getPackageName();
		this.methods = methods2stringSet(self.getMethods());
		
		this.supers = superclassNinterfaces();
		this.subs = new HashSet<String>();
	}
	
	private Set<String> methods2stringSet(Method[] methods) {
		Set<String> result = new HashSet<String>();
		for (int i = 0; i < methods.length; i ++) {
			String methodName = methods[i].getName();
			if (!NameHandler.shallExcludeMethod(methodName))
				result.add(methods[i].getName());
		}
		return result;
	}
	
	private Set<String> superclassNinterfaces() {
		Set<String> all = new HashSet<String>();
		String superclassname = self.getSuperclassName();
		if (superclassname != self.getClassName()
				&& !NameHandler.shallExcludeClass(superclassname))
			all.add(superclassname);
		for (String interfacename : self.getInterfaceNames())
			if (!NameHandler.shallExcludeClass(interfacename))
				all.add(interfacename);
		return all;
	}
	
	public JavaClass getJavaClass() {
		return this.self;
	}
	
	public boolean hasSuper(String superCandidiate) {
		return supers.contains(superCandidiate);
	}
	
	public boolean hasSub(String subCandidate) {
		return subs.contains(subCandidate);
	}
	
	public boolean hasMethod(String methodCandidate) {
		return methods.contains(methodCandidate);
	}

}
