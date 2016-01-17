package edu.ucsd.getty.callgraph;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.classfile.Method;

import edu.ucsd.getty.visitors.InvocationInstallationBinVisitor;

/**
 * Construct call graph from class folders, zips and/or jars. 
 * The result(s) will be combined into one call graph.
 * 
 */

public class CallGraphAnalyzer {
	//
	private String packagePrefix;
	
	public CallGraphAnalyzer(String pkgPrefix) {
		this.packagePrefix = pkgPrefix;
	}
	
	public CallGraphAnalyzer() {
		this("");
	}
	
	private void spread(String methodname, ClassInfo classinfo,
			Map<String, ClassInfo> classinfotable) {
		for (String subclassname : classinfo.subs) {
			if (classinfotable.keySet().contains(subclassname)) {				
				ClassInfo subclassinfo = classinfotable.get(subclassname);
				Set<String> subclassmethods = subclassinfo.methods;
				if (!subclassmethods.contains(methodname)) {
					subclassmethods.add(methodname);
					spread(methodname, subclassinfo, classinfotable);
				}
			}
		}
	}
	
	public CallGraph analyze(String... paths) {
		CallGraph callgraph = null;
		try {
			List<JavaClass> allClasses = ClassLocator.loadFrom(paths);
			Map<String, JavaClass> classTable = new HashMap<String, JavaClass>();
			Set<List<String>> staticInvocations = new HashSet<List<String>>();
			for (JavaClass clazz : allClasses) {
				InvocationInstallationBinVisitor visitor = 
						new InvocationInstallationBinVisitor(
								clazz, this.packagePrefix,
								classTable, staticInvocations);
				visitor.start();
			}
			
			Map<String, ClassInfo> classInfoTable = new HashMap<String, ClassInfo>();
			
			// first pass -- set self, pkg, cls, supers, methods
			for (String classname : classTable.keySet())
				classInfoTable.put(classname, new ClassInfo(classTable.get(classname)));
			
			Set<String> allclassnames = classInfoTable.keySet();
			
			// second pass -- set subs, non-recursively, one level down only for each class
			for (String classname : allclassnames) {
				ClassInfo classinfo = classInfoTable.get(classname);
				for (String superclassname : classinfo.supers) {
					if (allclassnames.contains(superclassname)
							&& !NameHandler.shallExcludeClass(superclassname))
						classInfoTable.get(superclassname).subs.add(classname);
				}
			}
			
			// third pass -- set methods, recursively for all sub levels for each class
			for (String classname : allclassnames) {
				ClassInfo classinfo = classInfoTable.get(classname);
				for (Method method : classinfo.getJavaClass().getMethods()) {
					if (!method.isPrivate()) {
						String methodname = method.getName();
						spread(methodname, classinfo, classInfoTable);
					}
				}
			}
			
			callgraph = new CallGraph(staticInvocations, classInfoTable);
			
			return callgraph;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}

    public static void main(String[] args) {
    	CallGraphAnalyzer analyzer = new CallGraphAnalyzer("org.apache.commons");
    	
    	CallGraph cg = analyzer.analyze(
    			"/Users/yanyan/Projects/research/eclipse/Getty/test/data/lib/test_email.jar",
    			"/Users/yanyan/Projects/studies/implementation_alt/commons-math/target/classes/");
    	
//    	for (String mtd : cg.staticCallersOf.keySet())
//    		System.out.println(cg.staticCallersOf.get(mtd) + " invoke " + mtd);
    	
    	for (String mtd : cg.possibleCallersOf.keySet())
    		System.out.println(cg.possibleCallersOf.get(mtd) + " invoke " + mtd);
    }
}
