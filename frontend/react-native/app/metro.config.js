const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);

// TypeScript 설정 추가
config.resolver.sourceExts = ['jsx', 'js', 'ts', 'tsx', 'json'];
config.resolver.assetExts = [...config.resolver.assetExts, 'cjs', 'png', 'jpg', 'jpeg', 'gif'];

// styled-components 관련 설정 추가
config.resolver.extraNodeModules = {
  ...config.resolver.extraNodeModules,
  'styled-components': require.resolve('styled-components'),
  'stylis': require.resolve('stylis'),
};

// 웹 플랫폼 설정 추가
config.transformer = {
  ...config.transformer,
  minifierPath: 'metro-minify-terser',
  minifierConfig: {
    // 웹 플랫폼 최적화
    ecma: 8,
    keep_classnames: true,
    keep_fnames: true,
    module: true,
    mangle: {
      module: true,
    },
  },
};

module.exports = config;
