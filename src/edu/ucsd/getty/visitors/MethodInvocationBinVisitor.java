package edu.ucsd.getty.visitors;

import java.util.Arrays;
import java.util.List;
import java.util.Set;

import org.apache.bcel.classfile.JavaClass;
import org.apache.bcel.generic.ConstantPoolGen;
import org.apache.bcel.generic.ConstantPushInstruction;
import org.apache.bcel.generic.EmptyVisitor;
import org.apache.bcel.generic.INVOKEINTERFACE;
import org.apache.bcel.generic.INVOKESPECIAL;
import org.apache.bcel.generic.INVOKESTATIC;
import org.apache.bcel.generic.INVOKEVIRTUAL;
import org.apache.bcel.generic.Instruction;
import org.apache.bcel.generic.InstructionConstants;
import org.apache.bcel.generic.InstructionHandle;
import org.apache.bcel.generic.MethodGen;
import org.apache.bcel.generic.ReturnInstruction;

import edu.ucsd.getty.callgraph.NameHandler;

/**
 * Print method invocations by their types.
 * 
 * Origin at CJKM: http://www.spinellis.gr/sw/ckjm/
 */
public class MethodInvocationBinVisitor extends EmptyVisitor {

    JavaClass visitedClass;
    private MethodGen mg;
    private ConstantPoolGen cpg;
//    private String methodInvokeFormatter;
    
    private String packagePrefix;
    
    private Set<List<String>> staticInvocations;

    public MethodInvocationBinVisitor(MethodGen m, JavaClass jc, 
    		String pkgPrefix, Set<List<String>> si) {
        visitedClass = jc;
        mg = m;
        cpg = mg.getConstantPool();
//        methodInvokeFormatter = (
//        		"[MTD] " + visitedClass.getClassName() + ":" + mg.getName() + " " + "(%s) %s:%s"
//        );
        this.packagePrefix = pkgPrefix;
        staticInvocations = si;
    }

    public void start() {
        if (mg.isAbstract() || mg.isNative())
            return;
        InstructionHandle ih = mg.getInstructionList().getStart();
        for (; ih != null; ih = ih.getNext()) {
            Instruction i = ih.getInstruction();
            
            if (!visitInstruction(i))
                i.accept(this);
        }
    }

    private boolean visitInstruction(Instruction i) {
        short opcode = i.getOpcode();

        return (InstructionConstants.INSTRUCTIONS[opcode] != null)
        		&& !(i instanceof ConstantPushInstruction)
        		&& !(i instanceof ReturnInstruction);
    }

    @Override
    public void visitINVOKEVIRTUAL(INVOKEVIRTUAL i) {
    	String classname = i.getReferenceType(cpg).toString();
    	String methodname = i.getMethodName(cpg);
    	if (classname.startsWith(packagePrefix) 
    			&& !NameHandler.shallExcludeClass(classname)
    			&& !NameHandler.shallExcludeMethod(methodname)) {
    		staticInvocations.add(Arrays.asList(new String[] {
    				"invokevirtual",
    				visitedClass.getClassName() + ":" + mg.getName(),
    				classname + ":" + methodname,
    		}));
//    		System.out.println(String.format(methodInvokeFormatter,
//    				"M-virtual",i.getReferenceType(cpg),i.getMethodName(cpg)));
    	}
    }

    @Override
    public void visitINVOKEINTERFACE(INVOKEINTERFACE i) {
    	String classname = i.getReferenceType(cpg).toString();
    	String methodname = i.getMethodName(cpg);
    	if (classname.startsWith(packagePrefix) 
    			&& !NameHandler.shallExcludeClass(classname)
    			&& !NameHandler.shallExcludeMethod(methodname)) {
    		staticInvocations.add(Arrays.asList(new String[] {
    				"invokeinterface",
    				visitedClass.getClassName() + ":" + mg.getName(),
    				classname + ":" + methodname,
    		}));
//    		System.out.println(String.format(methodInvokeFormatter,
//    				"I-interface",i.getReferenceType(cpg),i.getMethodName(cpg)));
    	}
    }

    @Override
    public void visitINVOKESPECIAL(INVOKESPECIAL i) {
    	String classname = i.getReferenceType(cpg).toString();
    	String methodname = i.getMethodName(cpg);
    	if (classname.startsWith(packagePrefix) 
    			&& !NameHandler.shallExcludeClass(classname)
    			&& !NameHandler.shallExcludeMethod(methodname)) {
    		staticInvocations.add(Arrays.asList(new String[] {
    				"invokespecial",
    				visitedClass.getClassName() + ":" + mg.getName(),
    				classname + ":" + methodname,
    		}));
//    		System.out.println(String.format(methodInvokeFormatter,
//    				"P-special",i.getReferenceType(cpg),i.getMethodName(cpg)));
    	}
    }
    
    @Override
    public void visitINVOKESTATIC(INVOKESTATIC i) {
    	String classname = i.getReferenceType(cpg).toString();
    	String methodname = i.getMethodName(cpg);
    	if (classname.startsWith(packagePrefix) 
    			&& !NameHandler.shallExcludeClass(classname)
    			&& !NameHandler.shallExcludeMethod(methodname)) {
    		staticInvocations.add(Arrays.asList(new String[] {
    				"invokestatic",
    				visitedClass.getClassName() + ":" + mg.getName(),
    				classname + ":" + methodname,
    		}));
//    		System.out.println(String.format(methodInvokeFormatter,
//    				"S-static",i.getReferenceType(cpg),i.getMethodName(cpg)));
    	}
    }
}
