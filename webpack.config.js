const path = require("path");

const CopyWebpackPlugin = require("copy-webpack-plugin");
const cssnano = require("cssnano");

const CleanWebpackPlugin = require("clean-webpack-plugin");
const OptimizeCssAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const context = path.resolve(__dirname, "./correspondence/static/src"); // the home directory for webpack

let plugins = [
  new CopyWebpackPlugin([
    {
      from: "./img/",
      to: "./build/img/"
    }
  ]),
  new CleanWebpackPlugin(["dist"]),
  new MiniCssExtractPlugin({
    filename: "build/css/[name].css",
    chunkFilename: "[id].css"
  })
];

const env = process.env.NODE_ENV || "development";

if (env == "production") {
  plugins = [
    ...plugins,
    new OptimizeCssAssetsPlugin({
      assetNameRegExp: /\.css$/g,
      cssProcessor: cssnano,
      cssProcessorOptions: { discardComments: { removeAll: true } },
      canPrint: true
    })
  ];
}

module.exports = {
  mode: process.env.NODE_ENV,
  optimization: {
    minimize: true
  },
  node: {
    fs: "empty"
  },
  context,
  entry: {
    app: ["./js/app.js"],
    main: ["./css/main.scss"],
    admin: ["./css/admin.scss"]
  },
  output: {
    path: path.resolve(__dirname, "correspondence/static"),
    filename: "build/js/[name].js"
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader"
      },
      {
        test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
        use: [
          {
            loader: "file-loader",
            options: {
              name: "[name].[ext]",
              outputPath: "./build/fonts/"
            }
          }
        ]
      },
      {
        test: /\.html$/,
        loader: "raw-loader"
      },
      {
        test: /\.(sass|scss)$/,
        use: [
          "style-loader",
          {
            loader: MiniCssExtractPlugin.loader
          },
          "css-loader",
          "postcss-loader",
          "sass-loader"
        ]
      }
    ]
  },
  plugins: plugins,
  stats: {
    colors: true
  }
};
