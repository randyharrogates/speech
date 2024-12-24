/** @format */

// frontend/src/pages/Search.js
import React, { useState } from "react";
import axios from "axios";

function Search() {
	const [searchTerm, setSearchTerm] = useState("");
	const [transcriptions, setTranscriptions] = useState([]);

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
		<div className="container mt-5">
			<h2>Search Transcriptions</h2>
			<div className="card p-4">
				<div className="input-group mb-3">
					<input type="text" className="form-control" placeholder="Enter filename to search" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
					<button className="btn btn-secondary" onClick={handleSearch}>
						Search
					</button>
				</div>
				<ul className="list-group">
					{transcriptions.length === 0 ? (
						<li className="list-group-item text-center">No results found</li>
					) : (
						transcriptions.map((t, index) => (
							<li key={index} className="list-group-item">
								<strong>{t.filename}</strong>: {t.transcription}
							</li>
						))
					)}
				</ul>
			</div>
		</div>
	);
}

export default Search;
