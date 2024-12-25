/** @format */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import axios from "axios";
import Search from "./search";

// Mock axios for testing
jest.mock("axios");

describe("Search Component", () => {
	it("renders the Search component correctly", () => {
		render(<Search />);

		// Check if the search input and button are present
		expect(screen.getByPlaceholderText(/Enter filename to search/i)).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /Search/i })).toBeInTheDocument(); // For button
	});

	it("fetches transcriptions and displays them when a valid search term is provided", async () => {
		// Mock API response
		const mockData = [
			{ filename: "file1.mp3", transcription: "Transcription 1" },
			{ filename: "file2.mp3", transcription: "Transcription 2" },
		];
		axios.get.mockResolvedValue({ data: mockData });

		render(<Search />);

		// Simulate user typing a search term
		fireEvent.change(screen.getByPlaceholderText(/Enter filename to search/i), {
			target: { value: "file" },
		});

		// Simulate clicking the search button
		fireEvent.click(screen.getByRole("button", { name: /Search/i }));

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

		render(<Search />);

		// Simulate user typing a search term
		fireEvent.change(screen.getByPlaceholderText(/Enter filename to search/i), {
			target: { value: "nonexistentfile" },
		});

		// Simulate clicking the search button
		fireEvent.click(screen.getByRole("button", { name: /Search/i }));

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

		render(<Search />);

		// Simulate user typing a search term
		fireEvent.change(screen.getByPlaceholderText(/Enter filename to search/i), {
			target: { value: "file" },
		});

		// Simulate clicking the search button
		fireEvent.click(screen.getByRole("button", { name: /Search/i }));

		// Wait for the error to be logged
		await waitFor(() => {
			expect(console.error).toHaveBeenCalledWith("Error searching transcriptions", expect.any(Error));
		});

		// Restore console.error to its original state after test
		console.error.mockRestore();
	});
});
