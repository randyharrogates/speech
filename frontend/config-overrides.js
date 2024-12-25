/** @format */

module.exports = function override(config, env) {
	// Modify the Jest config here
	if (env === "test") {
		config.moduleNameMapper = {
			"^react-router-dom$": "<rootDir>/node_modules/react-router-dom",
		};
	}
	return config;
};
