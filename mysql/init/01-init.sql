-- FamilyBot 数据库初始化脚本

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS familybot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE familybot;

-- 设置时区
SET time_zone = '+08:00';

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    nickname VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    password_hash VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS characters (
    character_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    family_role VARCHAR(50),
    personality TEXT,
    voice_config TEXT,
    avatar_url VARCHAR(500),
    system_prompt TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_family_role (family_role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 对话表
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    character_id BIGINT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    emotion VARCHAR(50),
    intent VARCHAR(100),
    context JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(character_id) ON DELETE CASCADE,
    INDEX idx_user_character (user_id, character_id),
    INDEX idx_created_at (created_at),
    INDEX idx_message_type (message_type),
    INDEX idx_emotion (emotion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话记录表';

-- 插入默认角色数据
INSERT IGNORE INTO characters (character_id, name, family_role, personality, voice_config, avatar_url, system_prompt) VALUES
(1, '喜羊羊', '儿子', '成熟稳重，关心家庭，有责任感', 
 '{"voice": "onyx", "speed": 1.0}', 
 '/images/character_xiyang.png',
 '你是喜羊羊，用户的儿子，刚刚工作几年。你成熟稳重，关心家庭，有强烈的责任感。'),

(2, '美羊羊', '女儿', '温柔细心，善解人意，是父母的贴心小棉袄',
 '{"voice": "nova", "speed": 0.9}',
 '/images/character_meiyang.png', 
 '你是美羊羊，用户的女儿，25岁，刚参加工作不久。你温柔细心，善解人意，是父母的贴心小棉袄。'),

(3, '懒羊羊', '孙子', '活泼可爱，天真烂漫，充满童趣',
 '{"voice": "fable", "speed": 1.1}',
 '/images/character_lanyang.png',
 '你是懒羊羊，用户的孙子，8岁，活泼可爱，天真烂漫，充满童趣。');

-- 插入测试用户数据  
INSERT IGNORE INTO users (user_id, username, nickname, avatar_url, password_hash) VALUES
(1, 'test_user', '测试用户', '/images/user_default.png', 'dummy_hash'),
(2, 'grandpa', '爷爷', '/images/user_grandpa.png', 'dummy_hash'),
(3, 'grandma', '奶奶', '/images/user_grandma.png', 'dummy_hash');

-- 创建视图：用户对话统计
CREATE OR REPLACE VIEW user_conversation_stats AS
SELECT 
    u.user_id,
    u.username,
    u.nickname,
    COUNT(c.conversation_id) as total_conversations,
    COUNT(DISTINCT c.character_id) as characters_chatted,
    DATE(MAX(c.created_at)) as last_chat_date
FROM users u
LEFT JOIN conversations c ON u.user_id = c.user_id
GROUP BY u.user_id, u.username, u.nickname;

-- 创建视图：角色受欢迎程度统计  
CREATE OR REPLACE VIEW character_popularity_stats AS
SELECT 
    ch.character_id,
    ch.name,
    ch.family_role,
    COUNT(c.conversation_id) as total_conversations,
    COUNT(DISTINCT c.user_id) as unique_users,
    DATE(MAX(c.created_at)) as last_used_date
FROM characters ch
LEFT JOIN conversations c ON ch.character_id = c.character_id  
GROUP BY ch.character_id, ch.name, ch.family_role;

-- 显示初始化完成信息
SELECT 'FamilyBot 数据库初始化完成！' as message;
