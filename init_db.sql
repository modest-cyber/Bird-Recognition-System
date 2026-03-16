-- ============================================================
-- 鸟类识别系统 数据库初始化脚本
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS bird_recognition
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bird_recognition;

-- 删除已存在的表（按依赖顺序）
DROP TABLE IF EXISTS bird_region;
DROP TABLE IF EXISTS record;
DROP TABLE IF EXISTS bird;
DROP TABLE IF EXISTS user;

-- 创建用户表
CREATE TABLE user (
    id          INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username    VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password    VARCHAR(255) NOT NULL COMMENT '密码（bcrypt加密）',
    email       VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    role        ENUM('user', 'admin') DEFAULT 'user' COMMENT '角色',
    is_active   BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 创建鸟类表
CREATE TABLE bird (
    id          INT PRIMARY KEY AUTO_INCREMENT COMMENT '鸟类ID',
    name        VARCHAR(100) NOT NULL COMMENT '中文名',
    latin_name  VARCHAR(100) COMMENT '学名',
    family      VARCHAR(100) COMMENT '科目',
    description TEXT COMMENT '特征描述',
    image_url   VARCHAR(255) COMMENT '示例图片路径',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_name (name),
    INDEX idx_family (family)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='鸟类表';

-- 创建识别记录表
CREATE TABLE record (
    id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id         INT NOT NULL COMMENT '用户ID',
    image_url       VARCHAR(255) NOT NULL COMMENT '上传图片路径',
    annotated_url   VARCHAR(255) COMMENT '标注图片路径',
    result_json     JSON NOT NULL COMMENT 'YOLOv8识别结果',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='识别记录表';

-- 创建鸟类分布表
CREATE TABLE bird_region (
    id      INT PRIMARY KEY AUTO_INCREMENT COMMENT '分布ID',
    bird_id INT NOT NULL COMMENT '鸟类ID',
    region  VARCHAR(100) NOT NULL COMMENT '分布地区',
    FOREIGN KEY (bird_id) REFERENCES bird(id) ON DELETE CASCADE,
    INDEX idx_bird_id (bird_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='鸟类分布表';

-- 插入默认管理员（密码: admin123）
INSERT INTO user (username, password, email, role) VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qwIlQwWPfMKjHu',
    'admin@birdrecognition.com',
    'admin'
);

-- 插入示例鸟类数据
INSERT INTO bird (name, latin_name, family, description, image_url) VALUES
('白鹭', 'Egretta garzetta', '鹭科', '白鹭是一种中型涉禽，体长约60厘米，全身羽毛洁白，嘴黑色，腿黑色，趾黄色。', '/uploads/birds/egret.jpg'),
('麻雀', 'Passer montanus', '雀科', '麻雀是小型鸟类，体长约14厘米，背部褐色，腹部灰白色，脸颊有黑斑。', '/uploads/birds/sparrow.jpg'),
('喜鹊', 'Pica pica', '鸦科', '喜鹊体长约45厘米，羽毛黑白相间，尾巴长而有光泽，是常见的留鸟。', '/uploads/birds/magpie.jpg');

-- 插入鸟类分布数据
INSERT INTO bird_region (bird_id, region) VALUES
(1, '华东'), (1, '华南'), (1, '华中'),
(2, '全国各地'),
(3, '华北'), (3, '华东'), (3, '西北');

SELECT '数据库初始化完成！' AS message;
