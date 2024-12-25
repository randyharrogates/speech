/** @format */
import React, { useState } from "react";
import axios from "axios";

function Upload() {
	const [files, setFiles] = useState([]);

	const handleFileUpload = async () => {
		if (files.length === 0) {
			alert("Please select at least one file to upload.");
			return;
		}

		const formData = new FormData();

		// Append multiple files to the FormData object
		for (let i = 0; i < files.length; i++) {
			formData.append("files", files[i]);
		}

		try {
			const response = await axios.post("http://localhost:8000/transcribe-multiple", formData, {
				headers: { "Content-Type": "multipart/form-data" },
			});
			alert("Files uploaded and transcribed!"); // If you want to display an alert
			console.log(response.data); // Display response data
		} catch (err) {
			console.error("Error during file upload", err);
			alert("Error during file upload"); // Handle the error alert
		}
	};

	const handleFileSelection = (e) => {
		// Append newly selected files to the existing array of files
		const selectedFiles = Array.from(e.target.files);
		setFiles((prevFiles) => [...prevFiles, ...selectedFiles]);
	};

	return (
		<div className="container mt-5">
			<h2>Upload and Transcribe</h2>
			<p>* Select one or more files</p>
			<div className="card p-4">
				<div className="mb-3">
					{/* Added the data-testid attribute for testing purposes */}
					<input
						type="file"
						className="form-control"
						multiple // Allow multiple file selection
						onChange={handleFileSelection}
						data-testid="file-input" // Ensure it's referenced in tests
					/>
				</div>
				<button className="btn btn-primary" onClick={handleFileUpload}>
					Upload and Transcribe
				</button>

				{/* Display selected files */}
				{files.length > 0 && (
					<div className="mt-4">
						<h5>Selected Files:</h5>
						<ul className="list-group">
							{files.map((file, index) => (
								<li key={index} className="list-group-item">
									{file.name}
								</li>
							))}
						</ul>
					</div>
				)}
			</div>
		</div>
	);
}

export default Upload;
