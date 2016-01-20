package edu.ucsd.getty.callgraph;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class CallGraph {
	
	protected Set<String> methods;
	
	protected Map<String, Set<String>> staticCallersOf;
	protected Map<String, Set<String>> possibleCallersOf;
	
	protected Map<String, Set<String>> staticCalleesOf;
	protected Map<String, Set<String>> possibleCalleesOf;
	
	private Set<List<String>> static_invocations;
	private Map<String, ClassInfo> class_info_table;

	public CallGraph(
			Set<List<String>> staticInvocations,
			Map<String, ClassInfo> classInfoTable) {
		
		this.methods = new HashSet<String>();
		this.staticCallersOf = new HashMap<String, Set<String>>();
		this.possibleCallersOf = new HashMap<String, Set<String>>();
		this.staticCalleesOf = new HashMap<String, Set<String>>();
		this.possibleCalleesOf = new HashMap<String, Set<String>>();
		
		this.static_invocations = staticInvocations;
		this.class_info_table = classInfoTable;

		for (List<String> invocation : this.static_invocations) {
			try {
				processInvocation(invocation);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}
	
	public Set<String> getStaticCallersOf(String fullMethodName) {
		Set<String> staticCallers = this.staticCallersOf.get(fullMethodName);
		if (staticCallers == null)
			return new HashSet<String>();
		else
			return staticCallers;
	}
	
	public Set<String> getPossibleCallersOf(String fullMethodName) {
		Set<String> possibleCallers = this.possibleCallersOf.get(fullMethodName);
		if (possibleCallers == null)
			return new HashSet<String>();
		else
			return possibleCallers;
	}
	
	private void processInvocation(List<String> invocation) throws Exception {
		String invokeType = invocation.get(0);
		
		String caller = invocation.get(1);
		String callee = invocation.get(2);		
		
		switch (invokeType) {
			case "invokestatic":
			case "invokespecial":
				install_static(caller, callee);
				break;
			case "invokeinterface":
			case "invokevirtual":
				String callerClass = NameHandler.extractClassName(caller);
				String callerMethod = NameHandler.extractMethodName(caller);
				String calleeClass = NameHandler.extractClassName(callee);
				String calleeMethod = NameHandler.extractMethodName(callee);
				install_dynamic(
						caller, callerClass, callerMethod, 
						callee, calleeClass, calleeMethod);
				break;
			default:
				throw new Exception("incorrect invocation type: " + invokeType);
		}
	}
	
	private void set_into(Map<String, Set<String>> target, String subject, String object) {
		Set<String> target_set = target.get(subject);
		if (target_set == null) {
			target_set = new HashSet<String>();
			target_set.add(object);
			target.put(subject, target_set);
		} else
			target_set.add(object);
	}
	
	private void install_static(String caller, String callee) {
		this.methods.add(caller);
		this.methods.add(callee);
		
		// install caller of the callee
		set_into(this.staticCallersOf, callee, caller);
		set_into(this.possibleCallersOf, callee, caller);
		
		// install callee of the caller
		set_into(this.staticCalleesOf, caller, callee);
		set_into(this.possibleCalleesOf, caller, callee);
	}
	
	private void install_dynamic(
			String caller, String caller_class, String caller_method, 
			String callee, String callee_class, String callee_method) {
		install_static(caller, callee);
		
		Set<String> sub_callers = new HashSet<String>();
		find_sub_candidates(sub_callers, caller, caller_class, caller_method);
		
		Set<String> sub_callees = new HashSet<String>();
		find_sub_candidates(sub_callees, callee, callee_class, callee_method);
		
		for (String sub_caller : sub_callers) {			
			for (String sub_callee : sub_callees) {
				// more possible callees
				set_into(this.possibleCalleesOf, sub_caller, sub_callee);
				// more possible callers
				set_into(this.possibleCallersOf, sub_callee, sub_caller);				
			}
		}
		
	}
	
	// over completed
	// FIXME consider method overloading and modifiers
	private void find_sub_candidates(Set<String> candidate_set,
			String full_name, String class_name, String method_name) {
		if (class_info_table.keySet().contains(class_name)) {
			ClassInfo classinfo = this.class_info_table.get(class_name);
			if (classinfo.hasMethod(method_name)) {
				candidate_set.add(full_name);
				for (String sub : classinfo.subs) {
					find_sub_candidates(candidate_set,
							sub + ":" + method_name, sub, method_name);
				}
			}
		}
	}
	
}
