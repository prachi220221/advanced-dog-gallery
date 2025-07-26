-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS dog_gallery;

-- Select the database
USE dog_gallery;

-- Create 'breeds' table
CREATE TABLE IF NOT EXISTS breeds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Create 'images' table
CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT NOT NULL,
    breed_id INT,
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    FOREIGN KEY (breed_id) REFERENCES breeds(id) ON DELETE SET NULL
);

-- Create 'viewed' table for tracking views
CREATE TABLE IF NOT EXISTS viewed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT,
    view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create 'liked' table for tracking likes
CREATE TABLE IF NOT EXISTS liked (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT,
    like_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);
