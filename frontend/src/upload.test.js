/** @format */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Upload from "./upload";
import axios from "axios";

jest.mock("axios");

describe("Upload Component", () => {
	it("renders the Upload component correctly", () => {
		render(<Upload />);
		// Check if the "Upload and Transcribe" button is present
		const buttons = screen.getAllByText(/Upload and Transcribe/i);
		expect(buttons.length).toBe(2);
	});

	it("handles file selection correctly", () => {
		render(<Upload />);
		// Use getByTestId for file input to avoid issues with role-based queries
		const fileInput = screen.getByTestId("file-input");
		const file1 = new File(["dummy content"], "file1.mp3", { type: "audio/mp3" });
		const file2 = new File(["dummy content"], "file2.mp3", { type: "audio/mp3" });
		fireEvent.change(fileInput, { target: { files: [file1, file2] } });

		// Check if the selected files are displayed in the UI
		const fileListItems = screen.getAllByRole("listitem");
		expect(fileListItems.length).toBe(2); // Two files should be selected
		expect(fileListItems[0]).toHaveTextContent("file1.mp3");
		expect(fileListItems[1]).toHaveTextContent("file2.mp3");
	});

	it("alerts user when no file is selected", async () => {
		render(<Upload />);
		// Mock the alert function
		window.alert = jest.fn();

		// Simulate clicking the upload button without selecting any files
		fireEvent.click(screen.getByRole("button", { name: /Upload and Transcribe/i }));

		// Check if the alert was triggered with the correct message
		await waitFor(() => expect(window.alert).toHaveBeenCalledWith("Please select at least one file to upload."));
	});

	it("uploads and transcribes files", async () => {
		render(<Upload />);
		const mockPost = jest.fn().mockResolvedValue({ data: "Files uploaded and transcribed!" });
		axios.post = mockPost;

		// Simulate file selection
		const fileInput = screen.getByTestId("file-input");
		const file1 = new File(["dummy content"], "file1.mp3", { type: "audio/mp3" });
		fireEvent.change(fileInput, { target: { files: [file1] } });

		// Simulate clicking the upload button
		fireEvent.click(screen.getByRole("button", { name: /Upload and Transcribe/i }));

		// Wait for the mock function to be called
		await waitFor(() => expect(mockPost).toHaveBeenCalled());
		// Check if the success message is correctly triggered
		expect(mockPost).toHaveBeenCalledWith(expect.any(String), expect.any(FormData), expect.any(Object));
	});
});
