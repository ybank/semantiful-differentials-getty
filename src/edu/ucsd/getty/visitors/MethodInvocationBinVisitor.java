package edu.ucsd.getty.visitors;

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

/**
 * Print method invocations by their types.
 * 
 * Origin at CJKM: http://www.spinellis.gr/sw/ckjm/
 */
public class MethodInvocationBinVisitor extends EmptyVisitor {

    JavaClass visitedClass;
    private MethodGen mg;
    private ConstantPoolGen cpg;
    private String methodInvokeFormatter;

    public MethodInvocationBinVisitor(MethodGen m, JavaClass jc) {
        visitedClass = jc;
        mg = m;
        cpg = mg.getConstantPool();
        methodInvokeFormatter = (
        		"[MTD] " + visitedClass.getClassName() + ":" + mg.getName() + " " + "(%s) %s:%s"
        );
    }

    public void start() {
        if (mg.isAbstract() || mg.isNative())
            return;
        for (InstructionHandle ih = mg.getInstructionList().getStart(); 
                ih != null; ih = ih.getNext()) {
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
        System.out.println(String.format(methodInvokeFormatter,"M-VTL",i.getReferenceType(cpg),i.getMethodName(cpg)));
    }

    @Override
    public void visitINVOKEINTERFACE(INVOKEINTERFACE i) {
        System.out.println(String.format(methodInvokeFormatter,"I-ITF",i.getReferenceType(cpg),i.getMethodName(cpg)));
    }

    @Override
    public void visitINVOKESPECIAL(INVOKESPECIAL i) {
        System.out.println(String.format(methodInvokeFormatter,"P-SPL",i.getReferenceType(cpg),i.getMethodName(cpg)));
    }

    @Override
    public void visitINVOKESTATIC(INVOKESTATIC i) {
        System.out.println(String.format(methodInvokeFormatter,"S-STT",i.getReferenceType(cpg),i.getMethodName(cpg)));
    }
}
