//Read-me:
//Open FIJI2. Navigate to Plugins > Bio-Formats > Bio-Formats Plugins Configuration>Formats>Select your desired file format>Tick Windowless
//Untick this after running
Ch_lip = 2;		//this channel is used for tracking the GUV
Ch_RNA = 1;
Ch_brightfield = 3;

#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String (label = "File suffix", value = ".tif") suffix

// See also Process_Folder.py for a version of this code
// in the Python scripting language.

processFolder(input);

// function to scan folders/subfolders/files to find files with correct suffix
// then process each file with function processFile
function processFolder(input) {
	list = getFileList(input);   								// calls a function to retrieve a list of files and directories located at 'input' path, output is a list 
	list = Array.sort(list);									// sorts the list in alphabetic order
	for (i = 0; i < list.length; i++) { 						// looping through each element in the list
		if(File.isDirectory(input + File.separator + list[i]))  // checks if the concatenation of input path with the current element in list is a directory
			processFolder(input + File.separator + list[i]);   	// process this folder and go through it again
		if(endsWith(list[i], suffix))							//check if he current element ends with a prefixed suffix
			processFile(input, output, list[i]);    			// calls another function passing paths for input and output and the current list element as parameters
	}
}

function processFile(input, output, file) { 			// processes the file from input path, performs some processing and saves it to output path
	print(file); 										// prints the name of current file to console
	//output = input; 									// sets output parameter to value of input parameter ??? this doesn't make sense -> commented out
	open(input + File.separator + file);				// opens the path of the specified file
	titleoriginal = getTitle;
	run("Duplicate...", "duplicate");
	name = getTitle();									// retrieves the title
	
	Stack.setChannel(Ch_RNA);
    run("CRL BOP orange ");
    run("Enhance Contrast...", "saturated=1");
	Stack.setChannel(Ch_lip);
	run("CRL BOP blue ");
	run("Enhance Contrast...", "saturated=1");
	
	Property.set("CompositeProjection", "Sum");
	Stack.setDisplayMode("composite");
	Stack.setActiveChannels("110");
	 
	run("Make Composite");
    
    
    run("Scale Bar...", "width=10 height=50 thickness=10 font=40 bold overlay");
	
	saveAs("Jpeg", output+ File.separator + name);		// saves the file at the output path	
	close();											// closes the file
	// Do the processing here by adding your own code.
	// Leave the print statements until things work, then remove them.
    // THIS IS WHERE YOU CAN OPEN YOUR FILES, ETC AS YOU WANT
	print("Processing: " + input + File.separator + file);
	print("Saving to: " + output);
	
	close(titleoriginal);
}
