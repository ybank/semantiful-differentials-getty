package edu.ucsd.getty.comp;

import static org.junit.Assert.*;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.Test;

import edu.ucsd.getty.callgraph.NameHandler;

public class CandidateGeneratorTest {

	@Test
	public void test() {
		assert "somestring".startsWith("");
		
		Pattern p = Pattern.compile(".*\\$\\d+.*");
		Matcher m = p.matcher("a.adfsjl.df:access$1 and something");
		if (m.matches())
			System.out.println("good");
		else
			fail("Not yet implemented");
		
		
		Pattern pp = Pattern.compile(".*:access\\$\\d+");
		Matcher mm = pp.matcher("org.apache.commons.math3.analysis.function.Sigmoid:access$000");
		if (mm.matches())
			System.out.println("good");
		else
			fail("Not yet implemented");
		
		if (new String[0].length == 0)
			System.out.println("right");
		
		Set<String[]> arraySet = new HashSet<String[]>();
		
		arraySet.add(new String[]{"abc", "def", "ghi"});
		System.out.println(arraySet.size());
		
		arraySet.add(new String[]{"abc", "def", "ghi"});
		System.out.println(arraySet.size());
		
		String abc = "abc";
		String def = "def";
		String ghi = "ghi";
		
		arraySet.add(new String[]{abc, def, ghi});
		System.out.println(arraySet.size());
		
		String def2 = "def";
		arraySet.add(new String[]{abc, def2, ghi});
		System.out.println(arraySet.size());
		
		String def3 = def;
		arraySet.add(new String[]{abc, def3, ghi});
		System.out.println(arraySet.size());
		
		String abc2 = "abc";
		String[] full = new String[3];
		full[0] = abc2;
		full[1] = "def";
		full[2] = ghi;
		arraySet.add(full);
		System.out.println(arraySet.size());
		
		String[] full2 = new String[3];
		full2 = full;
		arraySet.add(new String[]{abc, def, ghi});
		System.out.println(arraySet.size());
		
		String ghi2 = "ghi";
		String[] full3 = new String[] {"abc", "def", ghi2};
		arraySet.add(new String[]{abc, def, ghi});
		System.out.println(arraySet.size());
		
		Set<String> ss = new HashSet<String>();
		ss.add("abc");
		ss.add(abc2);
		ss.add(abc);
		System.out.println(ss.size());
		
		System.out.println("using a new technique");
		
		Set<List<String>> listSet = new HashSet<List<String>>();
		listSet.add(Arrays.asList(abc, def, ghi));
		listSet.add(Arrays.asList(abc, def2, ghi));
		listSet.add(Arrays.asList("abc", def, ghi2));
		listSet.add(Arrays.asList(full));
		listSet.add(Arrays.asList(full2));
		System.out.println(listSet.size());
		
		System.out.println(Arrays.asList(full).get(1));
		
		Pattern methodp = Pattern.compile("(.*):(.*)");
		Matcher methodm = methodp.matcher("org.apache.commons.math3.geometry.euclidean.threed.OutlineExtractor$BoundaryProjector:addContribution");
		if (methodm.find()) {
			System.out.println(methodm.groupCount());
			System.out.println(methodm.group(1));
			System.out.println(methodm.group(2));
		}
		else
			fail("Not yet implemented");
		
		String methodname = "org.apache.commons.math3.geometry.euclidean.threed.OutlineExtractor$BoundaryProjector:addContribution";
		System.out.println(NameHandler.extractClassName(methodname));
		System.out.println(NameHandler.extractMethodName(methodname));
		
	}

}
