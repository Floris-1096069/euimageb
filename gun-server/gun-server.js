// gun-server.js
const Gun = require('gun');
const express = require('express');
const app = express();

const gun = Gun({ file: 'data.json' });

app.use(express.json());

// --- Helper to collect map data ---
function getMapData(node, callback) {
  const result = {};
  node.map().once((value, key) => {
    result[key] = (value && value.val) ? value.val() : value;
  });
  // GunDB is async, but we'll use a timeout as a simple workaround
  setTimeout(() => callback(result), 100);  // Wait for GunDB to populate the map
}

// --- REST Endpoints ---
// Get all boards
app.get('/gun/boards', (req, res) => {
  getMapData(gun.get('boards'), (data) => {
    res.status(200).json(data);
  });
});

// Get a board
app.get('/gun/boards/:board_name', (req, res) => {
  gun.get('boards').get(req.params.board_name).once((data) => {
    res.status(200).json((data && data.val) ? data.val() : data || {});
  });
});

// Get posts for a board
app.get('/gun/boards/:board_name/posts', (req, res) => {
  getMapData(gun.get('boards').get(req.params.board_name).get('posts'), (data) => {
    res.status(200).json(data);
  });
});

// Create a board
app.post('/gun/boards/:board_name', (req, res) => {
  gun.get('boards').get(req.params.board_name).put(req.body);
  res.status(200).json({ status: 'ok' });
});

// Create a post
app.post('/gun/boards/:board_name/posts/:post_id', (req, res) => {
  gun.get('boards').get(req.params.board_name).get('posts').get(req.params.post_id).put(req.body);
  res.status(200).json({ status: 'ok' });
});

// Clear database
app.post('/gun/clear', (req, res) => {
  getMapData(gun.get('boards'), (boards) => {
    Object.keys(boards).forEach((key) => {
      gun.get('boards').get(key).put(null);
    });
    res.status(200).json({ status: 'Database cleared' });
  });
});

app.listen(8080, () => {
  console.log('GunDB REST API running on http://localhost:8080/gun');
});