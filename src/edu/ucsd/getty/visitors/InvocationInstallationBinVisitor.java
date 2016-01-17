package edu.ucsd.getty.visitors;

import java.util.List;
import java.util.Map;
import java.util.Set;

//import org.apache.bcel.classfile.Constant;
//import org.apache.bcel.classfile.ConstantPool;
import org.apache.bcel.classfile.EmptyVisitor;
import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.classfile.Method;
import org.apache.bcel.generic.ConstantPoolGen;
import org.apache.bcel.generic.MethodGen;

import edu.ucsd.getty.callgraph.NameHandler;

public class InvocationInstallationBinVisitor extends EmptyVisitor {

    private JavaClass clazz;
    private ConstantPoolGen constants;
//    private String classReferenceFormatter;
    
    private String packagePrefix;
    private Map<String, JavaClass> classTable;
	private Set<List<String>> staticInvocations;
    
    public InvocationInstallationBinVisitor(JavaClass jc, 
    		String pkgPrefix,
    		Map<String, JavaClass> ct, 
    		Set<List<String>> si) {
        this.clazz = jc;
        this.packagePrefix = pkgPrefix;
        this.classTable = ct;
        this.staticInvocations = si;
        this.constants = new ConstantPoolGen(clazz.getConstantPool());
//        this.classReferenceFormatter = "[CLS] " + clazz.getClassName() + " ---may---> %s";
    }

    @Override
    public void visitJavaClass(JavaClass jc) {
    	
    	String clsName = jc.getClassName();
    	
        if (clsName.startsWith(packagePrefix) && !NameHandler.shallExcludeClass(clsName)) {
        	jc.getConstantPool().accept(this);
        	
        	if (!classTable.containsKey(clsName))
        		this.classTable.put(clsName, jc);
        	
        	Method[] methods = jc.getMethods();
        	for (Method method : methods) {
        		String methodName = method.getName();
        		if (!NameHandler.shallExcludeMethod(methodName)) {
        			method.accept(this);
        		}
        	}
        }
    }

//    @Override
//    public void visitConstantPool(ConstantPool constantPool) {
//        for (int i = 0; i < constantPool.getLength(); i ++) {
//            Constant constant = constantPool.getConstant(i);
//            if (constant != null && constant.getTag() == 7) {
//                String referencedClass = constantPool.constantToString(constant);
//                System.out.println(String.format(classReferenceFormatter, referencedClass));
//            }
//        }
//    }

    @Override
    public void visitMethod(Method method) {
        MethodGen mg = new MethodGen(method, clazz.getClassName(), constants);
        MethodInvocationBinVisitor visitor = new MethodInvocationBinVisitor(mg, clazz, packagePrefix, staticInvocations);
        visitor.start(); 
    }

    public void start() {
        visitJavaClass(clazz);
    }
}
