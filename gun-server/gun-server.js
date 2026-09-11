const Gun = require('gun');
const express = require('express');
const app = express();

app.use('/gun', Gun.serve);

const server = app.listen(8080, () => {
  console.log('GunDB server running on http://localhost:8080/gun');
});

Gun({ web: server });