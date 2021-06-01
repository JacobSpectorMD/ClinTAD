const path = require('path');
const glob = require('glob');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const devMode = process.env.NODE_ENV !== 'production';

function getEntries(pattern) {
  const entries = {};

  glob.sync(pattern).forEach((file) => {
    entries[file.replace('static/node/', '')] = path.join(__dirname, file);
  });
  console.log(entries);
  return entries;
}

module.exports = [{
  entry: ['./static/node/app.scss'],
  output: {
    // This is necessary for webpack to compile
    // But we never use style-bundle.js
    filename: './static/js/material.js',
    path: path.resolve(__dirname),
  },
  devServer: {
    contentBase: './dist',
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: './static/css/material.css',
      chunkFilename: '[id].css'
    })
  ],
  module: {
    rules: [
      {
        test: /\.scss$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: './static/css/material.css',
            },
          },
          { loader: 'extract-loader' },
          { loader: 'css-loader' },
          {
            loader: 'sass-loader',
            options: {
              // Prefer Dart Sass
              implementation: require('sass'),

              // See https://github.com/webpack-contrib/sass-loader/issues/804
              webpackImporter: false,
              sassOptions: {
                includePaths: ['./node_modules'],
              },
            },
          },
        ]
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
        sideEffects: true
      },
    ]
  },
},
{
    entry: getEntries('static/node/*.js'),
    watch: true,
    devtool: 'source-map',
    output: {
        filename: '[name]',
        path: path.resolve(__dirname, 'static', 'dist')
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            }
        ]
    },
    resolve: {
        extensions: [
            '.js'
        ]
    }
}
];