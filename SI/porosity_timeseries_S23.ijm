Stack.getDimensions(width, height, channels, slices, frames);
sigma=0.05;
name="Timeseries_4";
minr=5.5;
getPixelSize(unit, pw, ph, pd);
minr=round(1/pw*minr);
if ((minr % 2) == 1) {minr=minr-1;} 
maxr=minr*3;
incre=1;
res=minr*10;



for (i = 1; i<=frames; i++){
	print(i);
run("Duplicate...", "title="+name+"_"+i+" duplicate frames="+i);
selectWindow(name+"_"+i);
run("Duplicate...", "title=GUV duplicate channels=2");
selectWindow("GUV");
run("Convert to Mask");
selectWindow("GUV");
run("Hough Circle Transform","minRadius="+minr+", maxRadius="+maxr+", inc="+incre+", minCircles=1, maxCircles=100, threshold=0.3, resolution="+res+", ratio=1.0, bandwidth=10, local_radius=10,  reduce show_mask show_centroids results_table");

while(!isOpen("Results")) {wait(1000);};
	nRows = nResults;
	for (row = 0; row < nRows; row++) {
		R=getResult("Radius (microns)", row);
		if (R>=2.5) {
			X=getResult("X (microns)", row)-R;
			Y=getResult("Y (microns)", row)-R;

			X=1/pw*X;
			Y=1/pw*Y;
			D=1/pw*R*2;
			makeOval(X, Y, D, D);
			roiManager("add");
		}
	}
selectWindow("Results");
saveAs("Results", "F:/porosity_analysed/Results/"+name+"_"+i+"_Results.csv");
run("Clear Results");
close("Results");

while(!isOpen("Centroid overlay")) {wait(100);};
selectWindow("Centroid overlay");
saveAs("Tiff", "F:/porosity_analysed/Hough/"+name+"_"+i+"_Centroid overlay.tif");
close(name+"_"+i+"_Centroid overlay.tif");

while(!isOpen("Centroid map")) {wait(100);};
selectWindow("Centroid map");
saveAs("Tiff", "F:/porosity_analysed/Hough/Centroid map/"+name+"_"+i+"_Centroid map.tif");
close(name+"_"+i+"_Centroid map.tif");


close("GUV");





if (roiManager("Count")>0) {
roiManager("Save", "F:/porosity_analysed/ROIManager/RoiSet_"+name+"_"+i+".zip");
numROIs= roiManager("Count");
for (numberroi=0; numberroi< numROIs; numberroi++) {
			selectWindow(name+"_"+i);
			roiManager("select",numberroi);
			run("Duplicate...", "title=GUV_"+numberroi+" duplicate channels=1");
			roiManager("add");
			selectWindow("GUV_"+numberroi);
			saveAs("Tiff", "F:/porosity_analysed/ROI/"+name+"_"+i+"GUV_"+numberroi+".tif");
			selectWindow(name+"_"+i+"GUV_"+numberroi+".tif");
			
			roiManager("select",numberroi+numROIs);
			run("Gaussian Blur...", "sigma="+sigma+" scaled");
			roiManager("select",numberroi+numROIs);
			run("Convert to Mask");
			roiManager("select",numberroi+numROIs);
			run("Erode");
			run("Set Measurements...", "standard centroid center perimeter bounding fit shape feret's integrated skewness kurtosis area_fraction redirect=None decimal=3");
			roiManager("select",numberroi+numROIs);
			run("Measure");
			
			close(name+"_"+i+"GUV_"+numberroi+".tif");
}
selectWindow("Results");
saveAs("Results", "F:/porosity_analysed/Measurements/"+name+"_"+i+"_Measurements.csv");
run("Clear Results");
close("Results");

roiManager("deselect");
roiManager("delete");
}
close(name+"_"+i);

}

