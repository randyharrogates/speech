/** @format */

// frontend/src/App.js
import React, { useState } from "react";
import axios from "axios";

function App() {
	const [file, setFile] = useState(null);
	const [transcriptions, setTranscriptions] = useState([]);
	const [searchTerm, setSearchTerm] = useState("");

	// Handle file upload
	const handleFileUpload = async (e) => {
		const formData = new FormData();
		formData.append("file", file);

		try {
			const response = await axios.post("http://localhost:8000/transcribe", formData, {
				headers: { "Content-Type": "multipart/form-data" },
			});
			alert("File uploaded and transcribed!");
		} catch (err) {
			console.error("Error during file upload", err);
		}
	};

	// Fetch all transcriptions
	const fetchTranscriptions = async () => {
		try {
			const response = await axios.get("http://localhost:8000/transcriptions");
			setTranscriptions(response.data);
		} catch (err) {
			console.error("Error fetching transcriptions", err);
		}
	};

	// Search transcriptions
	const handleSearch = async () => {
		try {
			const response = await axios.get("http://localhost:8000/search", {
				params: { filename: searchTerm },
			});
			setTranscriptions(response.data);
		} catch (err) {
			console.error("Error searching transcriptions", err);
		}
	};

	return (
		<div className="App">
			<h1>Audio Transcription</h1>

			<input type="file" onChange={(e) => setFile(e.target.files[0])} />
			<button onClick={handleFileUpload}>Upload and Transcribe</button>

			<h2>Search Transcriptions</h2>
			<input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
			<button onClick={handleSearch}>Search</button>

			<h2>Transcriptions</h2>
			<button onClick={fetchTranscriptions}>Get All Transcriptions</button>
			<ul>
				{transcriptions.map((transcription, index) => (
					<li key={index}>
						<strong>{transcription.filename}</strong>: {transcription.transcription}
					</li>
				))}
			</ul>
		</div>
	);
}

export default App;
