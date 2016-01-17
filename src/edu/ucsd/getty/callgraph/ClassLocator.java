package edu.ucsd.getty.callgraph;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipException;
import java.util.zip.ZipFile;

import org.apache.bcel.classfile.ClassParser;
import org.apache.bcel.classfile.JavaClass;

public class ClassLocator {

	private static void loadFromZoJIntoList(File zoj, List<JavaClass> all) throws ZipException, IOException {
		// It is known that f is either a zip or a jar file.
		ClassParser cp;
		ZipFile zipojar = new ZipFile(zoj);
		Enumeration<? extends ZipEntry> entries = zipojar.entries();
		while (entries.hasMoreElements()) {
			ZipEntry entry = entries.nextElement();
			if (!entry.isDirectory() && entry.getName().endsWith(".class")) {
				cp = new ClassParser(zoj.getPath(), entry.getName());
				all.add(cp.parse());
			}
		}
		zipojar.close();
	}
	
	private static void loadFromDirIntoList(File f, List<JavaClass> all) throws ZipException, IOException {
		// It is known that f is either a directory or a file
		File[] files = f.listFiles();
		if (files == null) {
			String filename = f.getName();
			if (filename.endsWith(".class")) {
				ClassParser cp = new ClassParser(f.getPath());
				all.add(cp.parse());
			} else if (filename.endsWith(".zip") || filename.endsWith(".jar")) {
				loadFromZoJIntoList(f, all);
			}
		} else {
			for (File element : files)
				loadFromDirIntoList(element, all);
		}
	}
	
	public static List<JavaClass> loadFrom(String... paths) throws ZipException, IOException {
		List<JavaClass> all = new ArrayList<JavaClass>();
		for (String path : paths) {
			File f = new File(path);
			if (!f.exists())
				throw new FileNotFoundException("The folder, zip or jar does not exist: " + path);
			if (f.isDirectory()) {
				loadFromDirIntoList(f, all);
			} else {
				loadFromZoJIntoList(f, all);
			}
		}
		return all;
	}

}
