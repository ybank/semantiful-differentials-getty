package edu.ucsd.getty.callgraph;

import java.io.File;
import java.util.Enumeration;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import org.apache.bcel.classfile.ClassParser;

import edu.ucsd.getty.visitors.ClassMethodMemberBinVisitor;

/**
 * Construct call graph from class folders, zips and/or jars. 
 * The result(s) will be combined into one call graph.
 * 
 */

public class CallGraphAnalyzer {
	
	public List<String> getClassUnder(String path) {
		return null;
	}
	
	public void analyze(String... paths) {		
		try {
			ClassParser cp;
			for (String path : paths) {
				
				File f = new File(path);
				if (!f.exists()) {
					throw new Exception("The folder, zip or jar does not exist: " + path);
				}
				
				if (f.isDirectory()) {
					// TODO: process folders
				} else {
					ZipFile zipojar = new ZipFile(f);
					Enumeration<? extends ZipEntry> entries = zipojar.entries();
					while (entries.hasMoreElements()) {
						ZipEntry entry = entries.nextElement();
						if (!entry.isDirectory() && entry.getName().endsWith(".class")) {
							cp = new ClassParser(path, entry.getName());
							ClassMethodMemberBinVisitor visitor = new ClassMethodMemberBinVisitor(cp.parse());
							visitor.start();
						}
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

    public static void main(String[] args) {
    	CallGraphAnalyzer analyzor = new CallGraphAnalyzer();
    	analyzor.analyze("test/data/lib/test_email.jar");
    }
}
