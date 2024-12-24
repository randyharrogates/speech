/** @format */

// frontend/src/pages/Upload.js
import React, { useState } from "react";
import axios from "axios";

function Upload() {
	const [file, setFile] = useState(null);

	const handleFileUpload = async () => {
		const formData = new FormData();
		formData.append("file", file);

		try {
			await axios.post("http://localhost:8000/transcribe", formData, {
				headers: { "Content-Type": "multipart/form-data" },
			});
			alert("File uploaded and transcribed!");
		} catch (err) {
			console.error("Error during file upload", err);
		}
	};

	return (
		<div className="container mt-5">
			<h2>Upload and Transcribe</h2>
			<div className="card p-4">
				<div className="mb-3">
					<input type="file" className="form-control" onChange={(e) => setFile(e.target.files[0])} />
				</div>
				<button className="btn btn-primary" onClick={handleFileUpload}>
					Upload and Transcribe
				</button>
			</div>
		</div>
	);
}

export default Upload;
