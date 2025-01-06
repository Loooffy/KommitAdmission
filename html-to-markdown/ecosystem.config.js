module.exports = {
  apps: [{
    name: 'html-to-markdown',
    script: 'dist/main.js',
    watch: false,
    env: {
      NODE_ENV: 'production',
      TOGETHER_API_KEY: '6db3cb5c4a093b9890e6926e763a07d00f859b355a6bfbe15537a106ec5761e3'
    }
  }]
} 