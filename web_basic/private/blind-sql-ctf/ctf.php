<?php
// 데이터베이스 초기화
$db = new SQLite3('/tmp/ctf.db');

// 테이블 생성 및 데이터 삽입
$db->exec("
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        email TEXT,
        role TEXT,
        join_date TEXT
    )
");

$db->exec("
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        title TEXT,
        content TEXT,
        author TEXT,
        created_at TEXT,
        category TEXT
    )
");

$db->exec("
    CREATE TABLE IF NOT EXISTS flags (
        id INTEGER PRIMARY KEY,
        flag_name TEXT,
        flag_value TEXT
    )
");

// 초기 데이터 삽입
$db->exec("DELETE FROM members");
$db->exec("DELETE FROM posts");
$db->exec("DELETE FROM flags");

$db->exec("INSERT INTO members (username, password, email, role, join_date) VALUES 
    ('admin', 'Wh01s_4dm1n_2024!', 'admin@whois.club', 'administrator', '2024-01-01'),
    ('alice', 'password123', 'alice@student.edu', 'member', '2024-03-15'),
    ('bob', 'qwerty456', 'bob@student.edu', 'member', '2024-05-20'),
    ('charlie', 'letmein789', 'charlie@student.edu', 'moderator', '2024-02-10'),
    ('david', 'secure_pass', 'david@student.edu', 'member', '2024-06-01')
");

$db->exec("INSERT INTO posts (title, content, author, created_at, category) VALUES 
    ('WHOIS 동아리 소개', 'WHOIS는 정보보안을 공부하는 동아리입니다.', 'admin', '2024-01-01 10:00:00', 'notice'),
    ('CTF 대회 안내', '이번 달 CTF 대회에 참가할 팀원을 모집합니다.', 'charlie', '2024-03-20 14:30:00', 'event'),
    ('Penetration Testing 스터디', 'Web Application 취약점 분석 스터디를 진행합니다.', 'alice', '2024-04-15 16:45:00', 'study'),
    ('네트워크 보안 세미나', '최신 네트워크 공격 기법에 대해 알아봅시다.', 'bob', '2024-05-10 11:20:00', 'seminar'),
    ('비밀 프로젝트 진행상황', '특별한 프로젝트가 진행 중입니다... 자세한 내용은 관리자만 볼 수 있습니다.', 'admin', '2024-06-01 09:15:00', 'secret')
");

$db->exec("INSERT INTO flags (flag_name, flag_value) VALUES 
    ('main_flag', 'CTF{WH01S_bl1nd_URL_1nj3ct10n_m4st3r}'),
    ('bonus_flag', 'CTF{URL_p4r4m3t3r_h4ck1ng_3xp3rt}')
");

// Time-based 블라인드 SQL 인젝션을 위한 sleep 함수 활성화
$db->createFunction('SLEEP', function($seconds) {
    sleep($seconds);
    return 1;
});

// URL 파라미터에서 사용자 ID 가져오기
$user_id = isset($_GET['user']) ? $_GET['user'] : '';
$posts = [];
$error_message = '';

if ($user_id) {
    try {
        // 취약한 쿼리 - 블라인드 SQL 인젝션 가능
        $query = "SELECT * FROM posts WHERE author = '$user_id' ORDER BY created_at DESC";
        
        $result = $db->query($query);
        
        if ($result) {
            while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
                $posts[] = $row;
            }
        }
        
        // 결과가 없어도 에러 메시지는 표시하지 않음 (블라인드 특성)
        
    } catch (Exception $e) {
        // 에러 메시지는 숨김 (블라인드 특성)
        $posts = [];
    }
}
?>

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WHOIS 동아리 게시판</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .search-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .search-form {
            display: flex;
            gap: 15px;
            align-items: center;
            justify-content: center;
        }
        
        .search-input {
            padding: 12px 20px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            width: 300px;
            transition: all 0.3s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }
        
        .search-btn {
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .members-list {
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .members-list h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .member-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .member-link {
            display: inline-block;
            padding: 8px 15px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 20px;
            border: 1px solid #667eea;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .member-link:hover {
            background: #667eea;
            color: white;
            transform: translateY(-1px);
        }
        
        .content {
            padding: 30px;
        }
        
        .posts-section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .post-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            margin-bottom: 20px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .post-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .post-title {
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .post-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #6c757d;
        }
        
        .post-content {
            color: #495057;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .category-tag {
            display: inline-block;
            padding: 4px 12px;
            background: #667eea;
            color: white;
            border-radius: 15px;
            font-size: 0.8em;
            text-transform: uppercase;
        }
        
        .no-posts {
            text-align: center;
            padding: 50px;
            color: #6c757d;
            font-size: 1.1em;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ WHOIS 동아리 게시판</h1>
            <p>정보보안 연구 동아리 - 함께 배우고 성장하는 보안 전문가들</p>
        </div>
        
        <div class="search-section">
            <form method="GET" class="search-form">
                <input type="text" name="user" class="search-input" 
                       placeholder="작성자 이름으로 게시글 검색..." 
                       value="<?php echo htmlspecialchars($user_id); ?>">
                <button type="submit" class="search-btn">🔍 검색</button>
            </form>
        </div>
        
        <div class="members-list">
            <h3>👥 동아리 멤버</h3>
            <div class="member-links">
                <a href="?user=admin" class="member-link">👑 admin</a>
                <a href="?user=alice" class="member-link">👩‍💻 alice</a>
                <a href="?user=bob" class="member-link">👨‍💻 bob</a>
                <a href="?user=charlie" class="member-link">⚡ charlie</a>
                <a href="?user=david" class="member-link">🚀 david</a>
            </div>
        </div>
        
        <div class="content">
            <div class="posts-section">
                <?php if ($user_id): ?>
                    <h2>📝 <?php echo htmlspecialchars($user_id); ?>님의 게시글</h2>
                    
                    <?php if (count($posts) > 0): ?>
                        <?php foreach ($posts as $post): ?>
                            <div class="post-card">
                                <div class="post-title"><?php echo htmlspecialchars($post['title']); ?></div>
                                <div class="post-meta">
                                    <span>👤 <?php echo htmlspecialchars($post['author']); ?></span>
                                    <span>📅 <?php echo htmlspecialchars($post['created_at']); ?></span>
                                    <span class="category-tag"><?php echo htmlspecialchars($post['category']); ?></span>
                                </div>
                                <div class="post-content"><?php echo htmlspecialchars($post['content']); ?></div>
                            </div>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <div class="no-posts">
                            <p>😔 해당 사용자의 게시글이 없습니다.</p>
                            <p>다른 멤버의 게시글을 확인해보세요!</p>
                        </div>
                    <?php endif; ?>
                <?php else: ?>
                    <h2>🏠 WHOIS 동아리에 오신 것을 환영합니다!</h2>
                    <div class="post-card">
                        <div class="post-title">동아리 소개</div>
                        <div class="post-content">
                            <p>WHOIS는 정보보안을 전문적으로 연구하는 동아리입니다.</p>
                            <p>웹 애플리케이션 보안, 네트워크 보안, 시스템 해킹 등 다양한 분야를 다룹니다.</p>
                            <p>위에서 멤버 이름을 클릭하거나 검색창을 사용하여 각 멤버의 게시글을 확인할 수 있습니다.</p>
                        </div>
                    </div>
                <?php endif; ?>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2024 WHOIS Security Club. 이 사이트는 교육 목적으로 제작되었습니다.</p>
        </div>
    </div>
</body>
</html>