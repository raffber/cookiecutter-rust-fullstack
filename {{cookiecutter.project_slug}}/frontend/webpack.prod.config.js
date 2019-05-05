const path = require('path');

module.exports = {
  entry: path.resolve(__dirname, "./js/app.js"),
  output: {
    webassemblyModuleFilename: "app.wasm",
    path: path.resolve(__dirname, "../build/prod/static"),
    filename: "app.js",
    publicPath: "/static/",
  },
  mode: "production",
  module: {
    rules: [
      {
        test: /\.(scss)$/,
        loaders: ["style-loader", "css-loader", "sass-loader"]
      },
    ]
  }
};
