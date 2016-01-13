package edu.ucsd.getty.comp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import soot.MethodOrMethodContext;
import soot.PackManager;
import soot.Scene;
import soot.SceneTransformer;
import soot.SootClass;
import soot.SootMethod;
import soot.Transform;
import soot.jimple.toolkits.callgraph.CHATransformer;
import soot.jimple.toolkits.callgraph.CallGraph;
import soot.jimple.toolkits.callgraph.Targets;
import soot.options.Options;
import edu.ucsd.getty.ITraceFinder;

public class CandidateGenerator implements ITraceFinder {
	
	private Set<String> changedMethods;
	private String binaryPath;

	public CandidateGenerator(Set<String> changed, String binaryPath) {
		this.changedMethods = changed;
		this.binaryPath = binaryPath;
	}

	@Override
	public Set<String> getCallersFor(String methodName) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Set<String> getAllCallers(Set<String> methodNames) {
		// TODO Auto-generated method stub
		return null;
	}
	
	public Set<String> getCallers() {
		return getAllCallers(this.changedMethods);
	}

	@Override
	public Set<String[]> getTraces(String methodName) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Set<String[]> getCandidateTraces(Set<String> methods) {
		// TODO Auto-generated method stub
		return null;
	}
	
	public Set<String[]> getCandidateTraces() {
		return getCandidateTraces(this.changedMethods);
	}
	
	public static void main(String[] args) {
		
		/**
		 * command to run this main:
		 * 		
		 * 		($process_dir = the directory to process
		 * 		 $mvn_build_path = the output of "mvn dependency:build-classpath"
		 * 		 $output_dir = the directory to place any output)
		 * 		
		 * 		java soot.Main -cp $process_dir:$mvn_build_path -pp -process-dir $process_dir -src-prec only-class -d $output_dir
		 * 
		 * 
		 * commands to get mvn variables:
		 * 
		 * 		($mvn_var is one of the following:
		 * 		 project.build.sourceDirectory
		 * 		 project.build.scriptSourceDirectory
		 * 		 project.build.testSourceDirectory
		 * 		 project.build.outputDirectory
		 * 		 project.build.testOutputDirectory
		 * 		 project.build.directory)
		 * 
		 * 		mvn help:evaluate -Dexpression=$mvn_var
		 * 
		 * command to build jar:
		 * 
		 * 		($target_jar_folder is the folder to save jar
		 * 		 $target_classes_folder is the folder with target classes)
		 * 
		 * 		jar cvf $target_jar_folder/target.jar -C $target_calsses_folder .
		 */
		
		// FIXME: this may have to be done at the target project if we use soot
		
		final String targetClass = "org.apache.commons.mail.HtmlEmail";
		final String targetMethod = "buildMimeMessage";
		
//		final String targetClass = "org.apache.commons.mail.Email";
//		final String targetMethod = "send";
		
//		final String targetClass = "org.apache.commons.mail.EmailUtils";
//		final String targetMethod = "notNull";
		
		List<String> argsList = new ArrayList<String>(Arrays.asList(args));
		argsList.addAll(Arrays.asList(new String[] {

				"-i", "org.apache.",
				"-include", "org.apache.",
				
				"-exclude", "java.",
				"-exclude", "javax.",
				"-exclude", "soot.",
				
				"-w", "-main-class", "edu.ucsd.getty.comp.CandidateGenerator",
				"edu.ucsd.getty.comp.CandidateGenerator",
				"org.apache.commons.mail.Email",
//				"org.apache.commons.mail.HtmlEmail"
		}));
		args = argsList.toArray(new String[0]);
		try{
			System.out.println("Getty - Candidate Generator");
			PackManager.v().getPack("wjtp").add(new Transform("wjtp.customentrycall", new SceneTransformer() {
				@Override
				protected void internalTransform(String phaseName, Map options) {
					CHATransformer.v().transform();
					
					SootClass tc = Scene.v().getSootClass(targetClass);
					tc.setResolvingLevel(SootClass.BODIES);
					
					System.out.println("Inside of the internal transformation ...");
					System.out.println("\napplication classes: " + Scene.v().getApplicationClasses() + "\n");
					
					CallGraph callGraph = Scene.v().getCallGraph();
					SootMethod target = tc.getMethodByName(targetMethod);
					
					
					Set<String> callerClassSet = new HashSet<String>();
					System.out.println("See all methods that have callee(s) in org.apache package:");
					int numberTargets = 0;
					Iterator<MethodOrMethodContext> targetMethod = callGraph.sourceMethods();
					while(targetMethod.hasNext()) {
						SootMethod tgt = (SootMethod) targetMethod.next();
						String signature = tgt.getSignature();
						if (signature.startsWith("<org.apache"))
							System.out.println("processing a caller: " + tgt.getSignature());
						int indexColon = signature.indexOf(":");
						String className = signature.substring(1, indexColon);
						callerClassSet.add(className);
						numberTargets ++;
						Iterator<MethodOrMethodContext> callees = new Targets(callGraph.edgesOutOf(tgt));
						while (callees.hasNext()) {
							SootMethod callee = (SootMethod) callees.next();
							if (signature.startsWith("<org.apache"))
								System.out.println(tgt + " may call " + callee);
						}
						tc.setResolvingLevel(SootClass.BODIES);
					}
					Set<String> prefix3Set = new HashSet<String>();
					for (String sig : callerClassSet) {
						if (sig.length() > 11)
							prefix3Set.add(sig.substring(0, 12));
						else
							prefix3Set.add(sig);
					}
					System.out.println("total number of common package/class/etc prefixes: " + prefix3Set.size());
					System.out.println("total number of methods having callees: " + numberTargets + "\n");
					
					
					System.out.println("call graph size: " + callGraph.size());
					System.out.println("target method is: " + target.getSignature());
					
					Iterator<MethodOrMethodContext> targetCallers = new Targets(callGraph.edgesInto(target));
					System.out.println("targetCallers is: " + targetCallers);
					while (targetCallers.hasNext()) {
						System.out.println("processing a caller");
						SootMethod tgt = (SootMethod) targetCallers.next();
						System.out.println(target + " may be called by " + tgt);
//						tc.setResolvingLevel(SootClass.BODIES);
					}
					
					Iterator<MethodOrMethodContext> targetCallees = new Targets(callGraph.edgesOutOf(target));
					System.out.println("targetCallees is: " + targetCallees);
					while (targetCallees.hasNext()) {
						System.out.println("processing a callee");
						SootMethod tgt = (SootMethod) targetCallees.next();
						System.out.println(target + " may call " + tgt);
//						tc.setResolvingLevel(SootClass.BODIES);
					}
					
					System.out.println("\n");
				}
			}));
			
			soot.Main.main(args);
			
			System.out.println("Getty - call graph analysis is done.");	
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
