-- ============================================================
-- ?????? ????????
-- ============================================================

CREATE DATABASE IF NOT EXISTS bird_recognition
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bird_recognition;

DROP TABLE IF EXISTS record;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id          INT PRIMARY KEY AUTO_INCREMENT COMMENT '??ID',
    username    VARCHAR(50) UNIQUE NOT NULL COMMENT '???',
    password    VARCHAR(255) NOT NULL COMMENT '???bcrypt???',
    email       VARCHAR(100) UNIQUE NOT NULL COMMENT '??',
    role        ENUM('user', 'admin') DEFAULT 'user' COMMENT '??',
    is_active   BOOLEAN DEFAULT TRUE COMMENT '????',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '????',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='???';

CREATE TABLE record (
    id                  INT PRIMARY KEY AUTO_INCREMENT COMMENT '??ID',
    user_id             INT NOT NULL COMMENT '??ID',
    image_url           VARCHAR(255) NOT NULL COMMENT '??????',
    annotated_image_url VARCHAR(255) COMMENT '??????',
    result_json         JSON NOT NULL COMMENT 'YOLO ????',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '????',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='?????';

INSERT INTO user (username, password, email, role) VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qwIlQwWPfMKjHu',
    'admin@birdrecognition.com',
    'admin'
);

SELECT '????????' AS message;
