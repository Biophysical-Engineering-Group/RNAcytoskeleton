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

sigma=0.05;
name=getTitle();
path=input;

waitForUser("Drawing ROIs - Draw ROI, add to manager (command T on Mac). Draw ALL desired ROIs FIRST, then click OK to continue.");
while (roiManager("count") == 0)  {
	waitForUser("Draw ROIs");
}
roiManager("Save", path+"/ROIManager/RoiSet_"+name+".zip");
numROIs= roiManager("Count");
for (numberroi=0; numberroi< numROIs; numberroi++) {
			selectWindow(name);
			roiManager("select",numberroi);
			run("Duplicate...", "title=GUV_"+numberroi+" duplicate channels=1");
			roiManager("add"); //so that the ROI position when cropping is kept
			selectWindow("GUV_"+numberroi);
			saveAs("Tiff", path+"/ROI/"+name+"GUV_"+numberroi+".tif");
			selectWindow(name+"GUV_"+numberroi+".tif");
			
			
			roiManager("select",numberroi+numROIs);
			run("Gaussian Blur...", "sigma="+sigma+" scaled");
			roiManager("select",numberroi+numROIs);
			run("Convert to Mask");
			roiManager("select",numberroi+numROIs);
			run("Erode");
			run("Set Measurements...", "standard centroid center perimeter bounding fit shape feret's integrated skewness kurtosis area_fraction redirect=None decimal=3");
			roiManager("select",numberroi+numROIs);
			waitForUser("Is this correct?");
			run("Measure");
			
			close(name+"GUV_"+numberroi+".tif");
}
roiManager("deselect");
roiManager("delete");

selectWindow("Results");
saveAs("Results", path+"/Measurements/"+name+"_Measurements.csv");
run("Clear Results");
close("Results");

close(name);

}

