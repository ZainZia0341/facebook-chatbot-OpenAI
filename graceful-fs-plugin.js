// graceful-fs-plugin.js
const fs = require('fs');
const gracefulFs = require('graceful-fs');

class GracefulFsPlugin {
  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options;
    this.commands = {
      gracefulfs: {
        lifecycleEvents: ['initialize'],
      },
    };

    this.hooks = {
      'before:deploy:initialize': this.initialize.bind(this),
    };
  }

  initialize() {
    gracefulFs.gracefulify(fs);
    this.serverless.cli.log('Graceful FS initialized');
  }
}

module.exports = GracefulFsPlugin;
