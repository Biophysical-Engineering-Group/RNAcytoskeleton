// set factor_px_um for each image

run("Clear Results");

#@ File (label = "Output directory", style = "directory") output

imagenumber=nImages;

Ch_track = 2;						//this channel is used for tracking the GUV (lipid stain)
Ch_analyze = 1;						//this channel is used to analzye the intensity (RNA filaments)
factor_px_um = 0.0660239;			//um per pixel  copy paste from Fiji > Image > Properties > Pixel Width
quotient_lines = 10;				//fraction of lines of all ROI points on membrane that get analysed 
Rec_width = 3/factor_px_um;			// width of analysed rectangle in um



for (i = 1; i < imagenumber+1; i++) {
	imagename = getTitle();
	savename=replace(imagename, ".czi", "");
	selectWindow(imagename);
	Stack.setChannel(Ch_track);
	run("Gaussian Blur...", "sigma=3 slice");
	Stack.setChannel(Ch_track);
	setAutoThreshold("Li dark no-reset");	
	run("Convert to Mask", "method=Li background=Dark calculate black create");
	
	
	
	run("Fill Holes", "slice");
	
	run("Erode", "slice");
	run("Erode", "slice");
	run("Erode", "slice");
	run("Erode", "slice");
	run("Erode", "slice");
	run("Erode", "slice");
	run("Erode", "slice");
	run("Erode", "slice");

	
	
	run("Analyze Particles...", "size=10-5000 display clear summarize overlay add composite slice");
	
	holdname = getTitle();
	selectWindow(holdname);
	
	run("Duplicate...", "duplicate channels=2");

	saveAs("tiff", output + File.separator +savename+"_ROI");
	close(savename+"_ROI.tif");
	

	run("Set Measurements...", "centroid redirect=None decimal=3");
	
	
	selectWindow("Results");
	Centroid_X = getResult("X", 0);
	Centroid_Y = getResult("Y", 0);
	
	run("Clear Results");
	
	updateResults();
	
	
	roiManager("select", 0);
	Roi.getCoordinates(xpoints, ypoints);
	
	m = lengthOf(xpoints);
	lines = m/quotient_lines; 
	for (j = 0; j < m; j++) {
    	setResult("X", j, xpoints[j]*factor_px_um);
   		setResult("Y", j, ypoints[j]*factor_px_um);
   		dist_sqr = Math.sqr(xpoints[j]*factor_px_um - Centroid_X) + Math.sqr(ypoints[j]*factor_px_um - Centroid_Y);
   		setResult("distance", j, Math.sqrt(dist_sqr));	
    }
    
    updateResults();
    
    setResult("Centroid_X", 0, Centroid_X);
	setResult("Centroid_Y", 0, Centroid_Y);
    
	
	updateResults();
	selectWindow("Results");
	
	selectWindow(imagename);
	Stack.setChannel(Ch_analyze);



	for (p = 0; p < lines; p++) {
		run("Line Width...", "line=6"); 
		roiManager("show all with labels");
		row = m / lines * p;
		diameter =  getResult("distance", row);
		scaling_factor = 2;
		ROI_X = getResult("X", row);
		ROI_Y = getResult("Y", row);
		ROI_X_red = Centroid_X + (ROI_X - Centroid_X) * 0.8;
		ROI_Y_red = Centroid_Y + (ROI_Y - Centroid_Y) * 0.8;
		
		makeRotatedRectangle(Centroid_X/factor_px_um, Centroid_Y/factor_px_um, ROI_X_red/factor_px_um, ROI_Y_red/factor_px_um, Rec_width);
		roiManager("add");
		setResult("Index_p", row, p);
	};	
	selectWindow("Results");
    saveAs("Results", output + File.separator +savename+"_Results_Coord.csv");
	run("Set Measurements...", "mean centroid area_fraction  redirect=None decimal=3");
	selectWindow(imagename);
	Stack.setChannel(Ch_analyze);
	
	for (r = 0; r < lines; r++) {
		roiManager("Select", r+1);
		run("Measure");
	}
	selectWindow("Results");
	saveAs("Results", output + File.separator +savename+"_Results_int.csv");
	
	close(imagename);
	close(holdname);
	roiManager("reset");
	
	}


run("Close All");
