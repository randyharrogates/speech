/** @format */

import React, { useState } from "react";
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

		try {
			const response = await axios.post("http://localhost:8000/transcribe", formData, {
				headers: { "Content-Type": "multipart/form-data" },
			});
			alert("Files uploaded and transcribed!");
			console.log(response.data);

			// Clear the selected files after successful upload
			setUploadFiles([]); // Clear the upload files state
		} catch (err) {
			console.error("Error during file upload", err);
			alert("Error during file upload");
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
		<div className="container mt-5">
			<h1 className="text-center mb-5">Audio Transcription System</h1>

			{/* Upload Section */}
			<div className="card p-4 mb-4">
				<h2>Upload and Transcribe</h2>
				<div className="mb-3">
					<input type="file" className="form-control" multiple onChange={handleFileSelection} />
				</div>
				<button className="btn btn-primary" onClick={handleFileUpload}>
					Upload and Transcribe
				</button>

				{uploadFiles.length > 0 && (
					<div className="mt-4">
						<h5>Selected Files:</h5>
						<ul className="list-group">
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
			<div className="card p-4 mb-4">
				<h2>Search Transcriptions</h2>
				<div className="input-group mb-3">
					<input type="text" className="form-control" placeholder="Enter filename to search" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
					<button className="btn btn-secondary" onClick={handleSearch}>
						Search
					</button>
				</div>

				{/* Clear All Search Results Button */}
				<button className="btn btn-danger mb-3" onClick={clearAllSearchResults}>
					Clear All Search Results
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
			<div className="card p-4">
				<h2>All Transcriptions</h2>
				<button className="btn btn-success mb-3" onClick={fetchTranscriptions}>
					Fetch All Transcriptions
				</button>

				{/* Clear All Transcriptions Button */}
				<button className="btn btn-danger mb-3" onClick={clearAllTranscriptions}>
					Clear All Transcriptions
				</button>

				{allTranscriptions.length === 0 ? (
					<p className="text-center">No transcriptions available</p>
				) : (
					<table className="table table-striped table-bordered">
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
