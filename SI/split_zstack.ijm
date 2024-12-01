//ADAPT NUMBER OF SLICES TO YOUR STACK 

number_of_slices = 21
imagename = getTitle();
for (i = 0; i < number_of_slices; i++) { 
	j = i+1;
	selectWindow(imagename);
	run("Duplicate...", "duplicate slices="+j);
	
}
		