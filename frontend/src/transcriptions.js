/** @format */

// frontend/src/pages/Transcriptions.js
import React, { useState } from "react";
import axios from "axios";

function Transcriptions() {
	const [transcriptions, setTranscriptions] = useState([]);

	// Fetch transcriptions from the backend
	const fetchTranscriptions = async () => {
		try {
			const response = await axios.get("http://localhost:8000/transcriptions");
			setTranscriptions(response.data);
		} catch (err) {
			console.error("Error fetching transcriptions", err);
		}
	};

	return (
		<div className="container mt-5">
			<h2 className="mb-4">All Transcriptions</h2>
			<div className="card p-4">
				<button className="btn btn-success mb-3" onClick={fetchTranscriptions}>
					Fetch All Transcriptions
				</button>
				{/* Bootstrap Table */}
				{transcriptions.length === 0 ? (
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
							{transcriptions.map((t, index) => (
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

export default Transcriptions;
