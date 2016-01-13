package edu.ucsd.getty.visitors;

import org.apache.bcel.classfile.Constant;
import org.apache.bcel.classfile.ConstantPool;
import org.apache.bcel.classfile.EmptyVisitor;
import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.classfile.Method;
import org.apache.bcel.generic.ConstantPoolGen;
import org.apache.bcel.generic.MethodGen;

public class ClassMethodMemberBinVisitor extends EmptyVisitor {

    private JavaClass clazz;
    private ConstantPoolGen constants;
    private String classReferenceFormatter;
    
    public ClassMethodMemberBinVisitor(JavaClass jc) {
        clazz = jc;
        constants = new ConstantPoolGen(clazz.getConstantPool());
        classReferenceFormatter = "[CLS] " + clazz.getClassName() + " %s";
    }

    @Override
    public void visitJavaClass(JavaClass jc) {
        jc.getConstantPool().accept(this);
        Method[] methods = jc.getMethods();
        System.out.println("==========");
        System.out.println("Class: " + jc.getClassName());
        System.out.println("Methods: ");
        for (Method method : methods) {
        	System.out.println(method.getName() + " **detail** " + method.getSignature());
        }
        System.out.println("**********");
        for (int i = 0; i < methods.length; i++)
            methods[i].accept(this);
    }

    @Override
    public void visitConstantPool(ConstantPool constantPool) {
        for (int i = 0; i < constantPool.getLength(); i++) {
            Constant constant = constantPool.getConstant(i);
            if (constant == null)
                continue;
            if (constant.getTag() == 7) {
                String referencedClass = constantPool.constantToString(constant);
                System.out.println(String.format(classReferenceFormatter, referencedClass));
            }
        }
    }

    @Override
    public void visitMethod(Method method) {
        MethodGen mg = new MethodGen(method, clazz.getClassName(), constants);
        MethodInvocationBinVisitor visitor = new MethodInvocationBinVisitor(mg, clazz);
        visitor.start(); 
    }

    public void start() {
        visitJavaClass(clazz);
    }
}
