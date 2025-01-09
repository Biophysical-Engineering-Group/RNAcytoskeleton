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

sigma=10; //sigma threshold for Gaussian blur
//Dialog.create("Input Channels");
	//			Dialog.addMessage("Please specify which channel is the GUV and which is RNA");
		//		Dialog.addMessage("");
			//	Dialog.addNumber("GUV Channel", 0);
		//		Dialog.addNumber("RNA Channel", 0);
		//		Dialog.show();
		//		Ch_GUV=Dialog.getNumber();
		//		Ch_RNA=Dialog.getNumber();
Ch_RNA=1;
Ch_GUV= 2; 
name=getTitle();
path=input;

//waitForUser("Drawing ROIs - Draw ROI, add to manager (command T on Mac). Draw ALL desired ROIs FIRST, then click OK to continue.");
//while (roiManager("count") == 0)  {
//	waitForUser("Draw ROIs");
//}

	//Imagewidth = getWidth;
  	//Imageheight = getHeight;
	//Stack.setChannel(Ch_GUV);
	//run("Duplicate...", "use");
	
	
	roiManager("reset");
	
	run("Duplicate...", "title=GUV duplicate channels="+Ch_GUV);
	
	
	selectWindow("GUV");
	//run("Auto Threshold", "method=MaxEntropy white");
	//run("Dilate");
	//run("Gaussian Blur...", "sigma="+sigma);
	//setOption("BlackBackground", true);
	//run("Convert to Mask");
	//run("Fill Holes");
	run("Auto Threshold", "method=Li white");
	run("Fill Holes");
	run("Erode");
	run("Gaussian Blur...", "sigma="+sigma);
	run("Convert to Mask");
	run("Analyze Particles...", "size=25-Infinity circularity=0.80-1.00 exclude clear add");
	
	selectWindow(name);
	roiManager("Show All");
	waitForUser("Fix the ROIs");
	reply=getBoolean("Do you want to proceed?", "Yes", "No");

    if (reply==1)    {
	
	roiManager("deselect");
	folder3 = path + File.separator + "MaskedGUV";
	File.makeDirectory(folder3);
	selectWindow("GUV");
	saveAs("PNG", path+"/MaskedGUV/GUV_"+name+".png");
	close("GUV_"+name+".png");
	
	

	//if (roiManager("count") > 1 || roiManager("count") == 0 )  {
	//	waitForUser("Draw ROI manually OR remove unwanted ROIs");
	//};
	//folder = getDirectory("Select a directory");
	folder = path + File.separator + "ROIManager";
	File.makeDirectory(folder);
	roiManager("Save", path+"/ROIManager/RoiSet_"+name+".zip");
	
	folder1 = path + File.separator + "Overlay";
	File.makeDirectory(folder1);
	
	folder2 = path + File.separator + "Results";
	File.makeDirectory(folder2);
	
	
	run("Plots...", "list");

numROIs= roiManager("Count");
for (numberroi=0; numberroi< numROIs; numberroi++) {
			x=0;
			y=0;
			radius = 0;
			
			selectWindow(name);
			run("Duplicate...", "title=test duplicate");
			selectWindow("test");
			run("Set Scale...", "distance=1 known=0 unit=pixel");
			run("Set Measurements...", "centroid fit decimal=0");
			roiManager("select",numberroi);
			run("Measure");
			radius = getResult("Major", 0)/2;
			x = getResult("X", 0);
			y = getResult("Y", 0);
			close("test");
			
			selectWindow(name);
			run("Duplicate...", "title=lipid duplicate channels="+Ch_GUV);
			selectWindow(name);
			run("Duplicate...", "title=RNA duplicate channels="+Ch_RNA);
			
			run("Clear Results");
			selectWindow("lipid");
		    roiManager("select",numberroi);
 		    run("Radial Profile", "x="+x+" y="+y+" radius="+radius+" use");
            selectWindow("Plot Values");
            saveAs("Results", path+"/Results/Plot_Values_GUV_"+name+"_"+numberroi+".csv");
            close("Plot_Values_GUV_"+name+"_"+numberroi+".csv");
            close("Radial Profile Plot");
            close("lipid");
            
            run("Clear Results");
            selectWindow("RNA");
            roiManager("select",numberroi);
 		    run("Radial Profile", "x="+x+" y="+y+" radius="+radius+" use");
            selectWindow("Plot Values");
            saveAs("Results", path+"/Results/Plot_Values_RNA_"+name+"_"+numberroi+".csv");
            close("Plot_Values_RNA_"+name+"_"+numberroi+".csv");
			close("RNA");
		
}


//draw a line around the detected GUV
for (numberroi=0; numberroi< numROIs; numberroi++) {
			selectWindow(name);	
			roiManager("select",numberroi);
			run("Add Selection...");	
}
selectWindow(name);
saveAs("PNG", path+"/Overlay/"+name+".png");

close(name+".png");
roiManager("reset");
    } else {
close("*");
roiManager("reset");
    }


}

			//make array to select all ROIs
			//array = newArray(numROIs);
 		    //for (q=0; q<array.length; q++) {
            //   array[q] = q;
  			//}
			//roiManager("select", array);
			
			
			//setBatchMode(true);
			//code
			//setBatchMode(false);


