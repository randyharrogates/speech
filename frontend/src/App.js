/** @format */

import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./navbar";
import Upload from "./upload";
import Search from "./search";
import Transcriptions from "./transcriptions";
import LandingPage from "./landingpage";

function App() {
	return (
		<Router>
			<Navbar />
			<Routes>
				<Route path="/" element={<LandingPage />} />
				<Route path="/upload" element={<Upload />} />
				<Route path="/search" element={<Search />} />
				<Route path="/transcriptions" element={<Transcriptions />} />
			</Routes>
		</Router>
	);
}

export default App;
