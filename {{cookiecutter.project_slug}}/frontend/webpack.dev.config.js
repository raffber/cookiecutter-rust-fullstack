const path = require('path');

module.exports = {
  entry: path.resolve(__dirname, "./js/app.js"),
  output: {
    webassemblyModuleFilename: "app.wasm",
    path: path.resolve(__dirname, "../build/static"),
    filename: "app.js",
    publicPath: "/static/",
  },
  mode: "development",
  devtool: "source-map",
  module: {
    rules: [
      {
        test: /\.(scss)$/,
        use: [{
          loader: "style-loader", options: {
              sourceMap: true
          }
        }, {
          loader: "css-loader", options: {
              sourceMap: true
          }
        }, {
          loader: "sass-loader", options: {
              sourceMap: true
          }
        }]
      },
    ]
  }
};
