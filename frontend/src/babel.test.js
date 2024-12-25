/** @format */

import React from "react";
import { render } from "@testing-library/react";

test("basic render test", () => {
	const { getByText } = render(<div>Hello World</div>);
	expect(getByText("Hello World")).toBeInTheDocument();
});
