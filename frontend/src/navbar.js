/** @format */

// frontend/src/components/Navbar.js
import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";

function Navbar() {
  return (
		<nav className="navbar navbar-expand-lg navbar-dark bg-dark">
			<div className="container">
				{/* Brand Link */}
				<Link className="navbar-brand" to="/">
					<i className="bi bi-music-note-list"></i> Audio Transcription
				</Link>

				{/* Toggler Button for small screens */}
				<button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
					<span className="navbar-toggler-icon"></span>
				</button>

				{/* Navbar Links */}
				<div className="collapse navbar-collapse" id="navbarNav">
					<ul className="navbar-nav ms-auto">
						{/* Upload and Transcribe */}
						<li className="nav-item">
							<Link className="nav-link" to="/upload">
								<i className="bi bi-upload"></i> Upload and Transcribe
							</Link>
						</li>
						{/* Search Transcriptions */}
						<li className="nav-item">
							<Link className="nav-link" to="/search">
								<i className="bi bi-search"></i> Search Transcriptions
							</Link>
						</li>
						{/* All Transcriptions */}
						<li className="nav-item">
							<Link className="nav-link" to="/transcriptions">
								<i className="bi bi-card-list"></i> All Transcriptions
							</Link>
						</li>
					</ul>
				</div>
			</div>
		</nav>
  );
}

export default Navbar;
