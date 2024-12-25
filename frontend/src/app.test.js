/** @format */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import axios from "axios";
import App from "./App";

// Mock axios for testing
jest.mock("axios");

describe("App Component", () => {
	// Test for Upload Component
	it("renders the Upload section and handles file selection and upload", async () => {
		const mockPost = jest.fn().mockResolvedValue({ data: "Files uploaded and transcribed!" });
		axios.post = mockPost;

		render(<App />);

		// Check if the "Upload and Transcribe" button is present
		expect(screen.getByRole("button", { name: /Upload and Transcribe/i })).toBeInTheDocument();

		// Simulate file selection
		const fileInput = screen.getByTestId("file-input");
		const file1 = new File(["dummy content"], "file1.mp3", { type: "audio/mp3" });
		fireEvent.change(fileInput, { target: { files: [file1] } });

		// Check if the file is displayed in the selected files list
		expect(screen.getByText("file1.mp3")).toBeInTheDocument();

		// Simulate clicking the upload button
		fireEvent.click(screen.getByRole("button", { name: /Upload and Transcribe/i }));

		// Wait for the mock function to be called and check if the file upload was successful
		await waitFor(() => expect(mockPost).toHaveBeenCalled());
		expect(mockPost).toHaveBeenCalledWith(expect.any(String), expect.any(FormData), expect.any(Object));

		// Check if the success message is correctly triggered
		expect(screen.getByRole("button", { name: /Upload and Transcribe/i })).toBeDisabled(); // Should be disabled during upload
	});

	// Test for Search Component
	it("fetches and displays transcriptions when a valid search term is provided", async () => {
		// Mock API response
		const mockData = [
			{ filename: "file1.mp3", transcription: "Transcription 1" },
			{ filename: "file2.mp3", transcription: "Transcription 2" },
		];
		axios.get.mockResolvedValue({ data: mockData });

		render(<App />);

		// Simulate user typing a search term
		fireEvent.change(screen.getByPlaceholderText(/Enter filename to search/i), {
			target: { value: "file" },
		});

		// Simulate clicking the search button
		fireEvent.click(screen.getByTestId("search-button"));

		// Wait for the transcriptions to be displayed
		await waitFor(() => {
			expect(screen.getByText(/file1.mp3/i)).toBeInTheDocument();
			expect(screen.getByText(/file2.mp3/i)).toBeInTheDocument();
			expect(screen.getByText(/Transcription 1/i)).toBeInTheDocument();
			expect(screen.getByText(/Transcription 2/i)).toBeInTheDocument();
		});
	});

	it("displays 'No results found' if no transcriptions match the search term", async () => {
		// Mock API response with no data
		axios.get.mockResolvedValue({ data: [] });

		render(<App />);

		// Simulate user typing a search term
		fireEvent.change(screen.getByPlaceholderText(/Enter filename to search/i), {
			target: { value: "nonexistentfile" },
		});

		// Simulate clicking the search button
		fireEvent.click(screen.getByTestId("search-button"));

		// Wait for the 'No results found' message to appear
		await waitFor(() => {
			expect(screen.getByText(/No results found/i)).toBeInTheDocument();
		});
	});

	it("handles error when the search request fails", async () => {
		// Mock API to simulate an error
		axios.get.mockRejectedValue(new Error("Error searching transcriptions"));

		// Mock console.error to catch error logs
		jest.spyOn(console, "error").mockImplementation(() => {});

		render(<App />);

		// Simulate user typing a search term
		fireEvent.change(screen.getByPlaceholderText(/Enter filename to search/i), {
			target: { value: "file" },
		});

		// Simulate clicking the search button
		fireEvent.click(screen.getByTestId("search-button"));

		// Wait for the error to be logged
		await waitFor(() => {
			expect(console.error).toHaveBeenCalledWith("Error searching transcriptions", expect.any(Error));
		});

		// Restore console.error to its original state after test
		console.error.mockRestore();
	});

	// Test for Transcriptions Component
	it("fetches and displays all transcriptions", async () => {
		// Mock API response
		const mockData = [
			{ filename: "file1.mp3", transcription: "Transcription 1", created_at: "2024-12-01T00:00:00Z" },
			{ filename: "file2.mp3", transcription: "Transcription 2", created_at: "2024-12-02T00:00:00Z" },
		];
		axios.get.mockResolvedValue({ data: mockData });

		render(<App />);

		// Simulate button click to fetch transcriptions
		fireEvent.click(screen.getByText(/Fetch All Transcriptions/i));

		// Wait for the transcriptions to be rendered
		await waitFor(() => {
			expect(screen.getByText(/file1.mp3/i)).toBeInTheDocument();
			expect(screen.getByText(/file2.mp3/i)).toBeInTheDocument();
			expect(screen.getByText(/Transcription 1/i)).toBeInTheDocument();
			expect(screen.getByText(/Transcription 2/i)).toBeInTheDocument();
		});
	});

	it("displays 'No transcriptions available' if no transcriptions are fetched", async () => {
		// Mock API response with empty data
		axios.get.mockResolvedValue({ data: [] });

		render(<App />);

		// Simulate button click to fetch transcriptions
		fireEvent.click(screen.getByText(/Fetch All Transcriptions/i));

		// Wait for the 'No transcriptions available' message
		await waitFor(() => {
			expect(screen.getByText(/No transcriptions available/i)).toBeInTheDocument();
		});
	});

	it("handles error fetching transcriptions", async () => {
		// Mock API to simulate error
		axios.get.mockRejectedValue(new Error("Error fetching transcriptions"));

		// Mock console.error to catch error logs
		jest.spyOn(console, "error").mockImplementation(() => {});

		render(<App />);

		// Simulate button click to fetch transcriptions
		fireEvent.click(screen.getByText(/Fetch All Transcriptions/i));

		// Wait for the error to be logged
		await waitFor(() => {
			expect(console.error).toHaveBeenCalledWith("Error fetching transcriptions", expect.any(Error));
		});

		// Restore console.error to its original state after test
		console.error.mockRestore();
	});
});
