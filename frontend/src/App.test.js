/** @format */

import React from "react";
import { render, screen } from "@testing-library/react";
import App from "./App"; // Import your App component

test("renders LandingPage component", () => {
	render(<App />);
	expect(screen.getByText(/Landing Page/i)).toBeInTheDocument();
});

test("renders Upload component", () => {
	render(<App />);
	expect(screen.getByText(/Upload and Transcribe/i)).toBeInTheDocument();
});

test("renders Search component", () => {
	render(<App />);
	expect(screen.getByText(/Search/i)).toBeInTheDocument();
});

test("renders Transcriptions component", () => {
	render(<App />);
	expect(screen.getByText(/All Transcriptions/i)).toBeInTheDocument();
});
