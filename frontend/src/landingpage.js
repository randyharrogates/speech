/** @format */

// frontend/src/pages/LandingPage.js
import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function LandingPage() {
	return (
		<div className="container d-flex flex-column align-items-center justify-content-center vh-100 text-center">
			<h1 className="mb-4">Welcome to Audio Transcription!</h1>
			<p className="mb-4">This platform allows you to seamlessly upload audio files, transcribe them into text, and search through your transcriptions.</p>
			<p className="mb-3">It’s fast, efficient, and designed for your convenience.</p>
			<Link to="/upload">
				<button className="btn btn-primary btn-lg mb-4">Get Started</button>
			</Link>

			<div className="about-me mt-5">
				<h3>About Me</h3>
				<p className="mb-3">Hi, I'm Randy, the creator of this platform. </p>
				<p className="mb-3">Connect with me on LinkedIn to learn more about my work and projects.</p>
				<a href="https://www.linkedin.com/in/randychan112" target="_blank" rel="noopener noreferrer" className="btn btn-outline-secondary">
					Visit My LinkedIn
				</a>
			</div>
		</div>
	);
}

export default LandingPage;
