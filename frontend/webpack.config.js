const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const isDevelopment = process.env.NODE_ENV !== 'production';

module.exports = {
  // Múltiplos pontos de entrada organizados por app e escopo
  entry: {
    // === PEDIDO APP ===
    // Client scope
    'pedido/client/checkout': './src/apps/pedido/client/checkout/index.js',
    'pedido/client/status': './src/apps/pedido/client/status/index.js',
    'pedido/client/historico': './src/apps/pedido/client/historico/index.js',
  },
  
  output: {
    path: path.resolve(__dirname, '../'),
    filename: (pathData) => {
      const parts = pathData.chunk.name.split('/');
      if (parts.length === 3) {
        // Ex: pedido/client/checkout -> apps/pedido/static/pedido/client/checkout/bundle.js
        const [app, scope, page] = parts;
        return `apps/${app}/static/${scope}/${page}/bundle.js`;
      } else if (parts.length === 2) {
        // Ex: shared/client/vendor -> apps/shared/static/shared/client/vendor/bundle.js
        const [app, type] = parts;
        return `apps/${app}/static/${type}/bundle.js`;
      }
      // Fallback
      return `apps/${pathData.chunk.name}/bundle.js`;
    },
    clean: false,
    publicPath: '/static/',
  },
  
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      },
      {
        test: /\.css$/,
        use: [
          isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      }
    ]
  },
  
  plugins: [
    ...(isDevelopment ? [] : [
      new MiniCssExtractPlugin({
        filename: 'apps/[name].bundle.css'
      })
    ])
  ],
  
  resolve: {
    extensions: ['.js', '.jsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@shared': path.resolve(__dirname, 'src/shared'),
      '@components': path.resolve(__dirname, 'src/shared/components'),
      '@services': path.resolve(__dirname, 'src/shared/services'),
      '@pedido': path.resolve(__dirname, 'src/apps/pedido'),
    }
  },
  
  optimization: {
    splitChunks: {
      cacheGroups: {
        clientVendor: {
          test: /node_modules/,
          name: 'shared/client/vendor',
          chunks: (chunk) => chunk.name && chunk.name.includes('/client/'),
          priority: 10,
          reuseExistingChunk: true
        },
        sharedComponents: {
          test: /src\/shared/,
          name: 'shared/components',
          chunks: 'all',
          priority: 5,
          minChunks: 2
        }
      }
    }
  },
  
  mode: isDevelopment ? 'development' : 'production',
  devtool: isDevelopment ? 'eval-source-map' : 'source-map',
};