// for moving built js and css files in a cross-platform way
// to a folder inside the backend directory, so that the backend can serve them


import fs from 'fs-extra';
import { fileURLToPath } from 'url';
import path from 'path';

// Get the current file path and directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sourceDir = path.join(__dirname, 'dist');
const targetDir = path.join(__dirname, '../backend/backend/dbay_control');

// Remove the target directory if it exists
fs.remove(targetDir)
  .then(() => {
    // Copy the source directory to the target directory
    return fs.copy(sourceDir, targetDir);
  })
  .then(() => {
    console.log('move-python completed successfully.');
  })
  .catch(err => {
    console.error('Error during move-python:', err);
  });