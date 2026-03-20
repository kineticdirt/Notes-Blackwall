"""
In-memory data for sample API (real-world style: posts, users, search).
"""
from __future__ import annotations

POSTS = [
    {"id": 1, "userId": 1, "title": "Getting started with the API", "body": "Use GET /api/posts to list all posts."},
    {"id": 2, "userId": 1, "title": "Search and filter", "body": "Use ?q= to search post titles and body."},
    {"id": 3, "userId": 2, "title": "User management", "body": "GET /api/users returns users; GET /api/users/1 returns one."},
    {"id": 4, "userId": 2, "title": "Best practices for REST", "body": "Prefer GET for read, POST for create. Use proper status codes."},
    {"id": 5, "userId": 1, "title": "Pagination and limits", "body": "Pass limit and offset for large lists."},
]

USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Carol", "email": "carol@example.com"},
]
