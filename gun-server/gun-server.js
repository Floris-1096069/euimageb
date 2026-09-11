const Gun = require('gun');

const gun = Gun({
    port: 8080,
    peers: [],
    file: 'data.json',
    web: true
});

console.log('GunDB running on port 8080');