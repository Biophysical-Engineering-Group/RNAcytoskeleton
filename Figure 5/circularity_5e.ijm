//Read-me:
//Open FIJI2. Navigate to Plugins > Bio-Formats > Bio-Formats Plugins Configuration>Formats>Select your desired file format>Tick Windowless
//Untick this after running

#@ File (label = "Input directory", style = "directory") input
//#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".czi") suffix

// See also Process_Folder.py for a version of this code
// in the Python scripting language.

processFolder(input);

// function to scan folders/subfolders/files to find files with correct suffix
//then process each file with function processFile
function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	for (i = 0; i < list.length; i++) {
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			processFile(input, list[i]);
	}
}


function processFile(input, file) {
	open(input + File.separator + file);
	name=getTitle();
	path=input;
	roiManager("reset");
	selectWindow(name);
	run("Analyze Particles...", "size=10-Infinity exclude clear add");
	numROIs= roiManager("Count");
	if (numROIs==1){
		selectWindow(name);
		roiManager("deselect");
		roiManager("Measure");
	}
	if (numROIs>1){
		selectWindow(name);
		roiManager("Show All");
		waitForUser("Fix the ROIs");
		reply=getBoolean("Do you want to proceed?", "Yes", "No");
	    if (reply==1)    {
	    selectWindow(name);
		roiManager("deselect");
		roiManager("Measure");
	    }
	}
	selectWindow("Results");
	saveAs("Results", input+File.separator+name+".csv");
	run("Clear Results");
	close(name);
}

		
