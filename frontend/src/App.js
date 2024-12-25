/** @format */

import React, { useState, useRef } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";

function App() {
	// States for Upload, Search, and Transcriptions
	const [files, setFiles] = useState([]);
	const [searchTerm, setSearchTerm] = useState(""); // Search term for filtering transcriptions
	const [allTranscriptions, setAllTranscriptions] = useState([]); // All fetched transcriptions
	const [searchTranscriptions, setSearchTranscriptions] = useState([]); // Search results for transcriptions
	const [uploadFiles, setUploadFiles] = useState([]); // Files selected for upload
	const [loading, setLoading] = useState(false); // Loading state for progress bar
	const [uploadProgress, setUploadProgress] = useState(0); // Progress state for upload

	// Reference to the file input field
	const fileInputRef = useRef();

	// Handle file selection for upload
	const handleFileSelection = (e) => {
		const selectedFiles = Array.from(e.target.files);
		setUploadFiles((prevFiles) => [...prevFiles, ...selectedFiles]);
	};

	// Remove file from the selected files list
	const handleFileRemove = (index) => {
		setUploadFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
	};

	// Handle file upload
	const handleFileUpload = async () => {
		if (uploadFiles.length === 0) {
			alert("Please select at least one file to upload.");
			return;
		}

		const formData = new FormData();
		// Append files to FormData
		for (let i = 0; i < uploadFiles.length; i++) {
			formData.append("files", uploadFiles[i]);
		}

		setLoading(true); // Show the loading bar
		setUploadProgress(0); // Reset progress

		try {
			// Start the file upload with progress tracking
			const response = await axios.post("http://localhost:8000/transcribe", formData, {
				headers: { "Content-Type": "multipart/form-data" },
				onUploadProgress: (progressEvent) => {
					if (progressEvent.total) {
						const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
						setUploadProgress(progress); // Update the progress bar
					}
				},
			});
			alert("Files uploaded and transcribed!");
			console.log(response.data);

			// Clear the selected files after successful upload
			setUploadFiles([]); // Clear the upload files state
			fileInputRef.current.value = ""; // Clear the file input field
		} catch (err) {
			console.error("Error during file upload", err);
			alert("Error during file upload");
		} finally {
			setLoading(false); // Hide the loading bar after upload completes
		}
	};

	// Handle search for transcriptions
	const handleSearch = async () => {
		try {
			if (!searchTerm) {
				setSearchTranscriptions([]); // Clear search results if no search term
				return;
			}

			// Make a request to the backend search endpoint
			const response = await axios.get("http://localhost:8000/search", {
				params: { filename: searchTerm }, // Send searchTerm as query parameter
			});

			// Set the search results in the state
			setSearchTranscriptions(response.data); // Update the search results
		} catch (err) {
			console.error("Error searching transcriptions", err);
		}
	};

	// Fetch all transcriptions
	const fetchTranscriptions = async () => {
		try {
			// Clear search results before fetching all transcriptions
			setSearchTerm(""); // Clear the search term
			setSearchTranscriptions([]); // Clear the search results

			const response = await axios.get("http://localhost:8000/transcriptions");
			setAllTranscriptions(response.data); // Update all transcriptions
		} catch (err) {
			console.error("Error fetching transcriptions", err);
		}
	};

	// Clear all transcriptions
	const clearAllTranscriptions = () => {
		setAllTranscriptions([]); // Clear all transcriptions state
	};

	// Clear all search results
	const clearAllSearchResults = () => {
		setSearchTerm(""); // Reset search term
		setSearchTranscriptions([]); // Clear search results
	};

	return (
		<div className="container mt-4">
			<h1 className="text-center mb-5">Audio Transcription System</h1>

			{/* Upload Section */}
			<div className="card p-3 mb-4 shadow-sm">
				<h2 className="h5">Upload and Transcribe</h2>
				<div className="mb-3">
					<input
						type="file"
						className="form-control form-control-sm"
						multiple
						onChange={handleFileSelection}
						ref={fileInputRef} // Reference the file input field
						data-testid="file-input"
					/>
				</div>
				<button
					className="btn btn-primary btn-sm"
					onClick={handleFileUpload}
					disabled={loading} // Disable button during upload
				>
					<i className="bi bi-cloud-upload"></i> Upload and Transcribe
				</button>

				{/* Display Loading Bar */}
				{loading && (
					<div className="mt-2">
						<progress value={uploadProgress} max="100" className="w-100" />
					</div>
				)}

				{uploadFiles.length > 0 && (
					<div className="mt-4">
						<h5 className="h6">Selected Files:</h5>
						<ul className="list-group list-group-flush">
							{uploadFiles.map((file, index) => (
								<li key={index} className="list-group-item d-flex justify-content-between align-items-center">
									{file.name}
									<button className="btn btn-danger btn-sm" onClick={() => handleFileRemove(index)}>
										<i className="bi bi-trash"></i>
									</button>
								</li>
							))}
						</ul>
					</div>
				)}
			</div>

			{/* Search Section */}
			<div className="card p-3 mb-4 shadow-sm">
				<h2 className="h5">Search Transcriptions</h2>
				<div className="input-group mb-3">
					<input type="text" className="form-control form-control-sm" placeholder="Enter filename to search" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
					<button className="btn btn-secondary btn-sm" onClick={handleSearch} data-testid="search-button">
						<i className="bi bi-search"></i> Search
					</button>
				</div>

				{/* Clear All Search Results Button */}
				<button className="btn btn-danger btn-sm mb-3" onClick={clearAllSearchResults}>
					<i className="bi bi-x-circle"></i> Clear All Search Results
				</button>

				<ul className="list-group">
					{searchTranscriptions.length === 0 ? (
						<li className="list-group-item text-center">No results found</li>
					) : (
						searchTranscriptions.map((t, index) => (
							<li key={index} className="list-group-item">
								<strong>{t.filename}</strong>: {t.transcription}
							</li>
						))
					)}
				</ul>
			</div>

			{/* Transcriptions Section */}
			<div className="card p-3 shadow-sm">
				<h2 className="h5">All Transcriptions</h2>
				<button className="btn btn-success btn-sm mb-3" onClick={fetchTranscriptions}>
					<i className="bi bi-arrow-clockwise"></i> Fetch All Transcriptions
				</button>

				{/* Clear All Transcriptions Button */}
				<button className="btn btn-danger btn-sm mb-3" onClick={clearAllTranscriptions}>
					<i className="bi bi-trash"></i> Clear All Transcriptions
				</button>

				{allTranscriptions.length === 0 ? (
					<p className="text-center">No transcriptions available</p>
				) : (
					<table className="table table-striped table-bordered table-sm">
						<thead className="thead-dark">
							<tr>
								<th>#</th>
								<th>Filename</th>
								<th>Transcription</th>
								<th>Created At</th>
							</tr>
						</thead>
						<tbody>
							{allTranscriptions.map((t, index) => (
								<tr key={index}>
									<td>{index + 1}</td>
									<td>{t.filename}</td>
									<td>{t.transcription}</td>
									<td>{new Date(t.created_at).toLocaleString()}</td>
								</tr>
							))}
						</tbody>
					</table>
				)}
			</div>
		</div>
	);
}

export default App;
