/** @format */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import axios from "axios";
import Transcriptions from "./Transcriptions";

// Mock axios for testing
jest.mock("axios");

describe("Transcriptions Component", () => {
	it("fetches transcriptions and displays them", async () => {
		// Mock API response
		const mockData = [
			{ filename: "file1.mp3", transcription: "Transcription 1", created_at: "2024-12-01T00:00:00Z" },
			{ filename: "file2.mp3", transcription: "Transcription 2", created_at: "2024-12-02T00:00:00Z" },
		];
		axios.get.mockResolvedValue({ data: mockData });

		render(<Transcriptions />);

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

		render(<Transcriptions />);

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

		render(<Transcriptions />);

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
