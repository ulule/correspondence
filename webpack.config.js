const path = require("path");

const CopyPlugin = require("copy-webpack-plugin");

const { CleanWebpackPlugin } = require("clean-webpack-plugin");

const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const source = path.resolve(__dirname, "./correspondence/static/src");
const dest = path.resolve(__dirname, "./correspondence/static/build");

let plugins = [
  new CopyPlugin({patterns: [
    {
      from: source + "/img/",
      to: dest + "/img/",
    },
  ]}),
  new CleanWebpackPlugin({
    cleanAfterEveryBuildPatterns: ["dist"],
  }),
  new MiniCssExtractPlugin({
    filename: "css/[name].css",
    chunkFilename: "[id].css",
  }),
];

const env = process.env.NODE_ENV || "development";

module.exports = {
  mode: process.env.NODE_ENV,
  optimization: {
    minimize: true,
  },
  entry: {
    app: [source + "/js/app.js"],
    main: [source + "/css/main.scss"],
    admin: [source + "/css/admin.scss"],
  },
  output: {
    path: dest,
    filename: "js/[name].js",
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
      {
        test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
        use: [
          {
            loader: "file-loader",
            options: {
              name: "[name].[ext]",
              outputPath: "./build/fonts/",
            },
          },
        ],
      },
      {
        test: /\.(sass|scss)$/,
        use: [
          "style-loader",
          {
            loader: MiniCssExtractPlugin.loader,
          },
          "css-loader",
          "postcss-loader",
          "sass-loader",
        ],
      },
    ],
  },
  plugins: plugins,
  stats: {
    colors: true,
  },
};
