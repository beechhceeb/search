const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: './src/static/js/index.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'static/js')
    },
    plugins: [
        new CopyWebpackPlugin({
            patterns: [
                { from: 'node_modules/piexifjs/piexif.js', to: 'piexifjs/piexif.js' },
                { from: 'node_modules/progressbar.js/dist/progressbar.js', to: 'progressbar.js/progressbar.js' }
            ]
        })
    ],
    mode: 'development'
};