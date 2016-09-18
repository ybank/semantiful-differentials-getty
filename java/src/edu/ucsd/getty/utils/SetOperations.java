package edu.ucsd.getty.utils;

import java.util.HashSet;
import java.util.Set;

public class SetOperations {

	public static Set<String> intersection(Set<String> a, Set<String> b) {
		// a intersect b
		Set<String> result = new HashSet<String>();
		for (String ele : a)
			if (b.contains(ele))
				result.add(ele);
		return result;
	}
	
	public static Set<String> union(Set<String> a, Set<String> b) {
		// a union b
		Set<String> result = new HashSet<String>();
		result.addAll(a);
		result.addAll(b);
		return result;
	}
	
	public static Set<String> difference(Set<String> a, Set<String> b) {
		// a minus b
		Set<String> result = new HashSet<String>();
		result.addAll(a);
		result.removeAll(b);
		return result;
	}
	
	public static Set<String> symmetric_difference(Set<String> a, Set<String> b) {
		// (a - b) union (b - a)
		Set<String> a_b = difference(a, b);
		Set<String> b_a= difference(b, a);
		Set<String> result = union(a_b, b_a);
		return result;
	}
	
}
