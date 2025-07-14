-- This is the schema definition for the comment table
CREATE TABLE comment (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    parent_comment_id INTEGER Default -1,
    user_id INTEGER,
    subreddit INTEGER,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    num_likes INTEGER DEFAULT 0,
    num_dislikes INTEGER DEFAULT 0,
    FOREIGN KEY(post_id) REFERENCES post(post_id),
    FOREIGN KEY(parent_comment_id) REFERENCES comment(comment_id),
    FOREIGN KEY(user_id) REFERENCES user(user_id)
);
