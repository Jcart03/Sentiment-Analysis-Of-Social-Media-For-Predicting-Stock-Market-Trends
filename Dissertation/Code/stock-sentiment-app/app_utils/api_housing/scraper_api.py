import pandas as pd
import praw
import time
from DTOs.Comment import CommentBatchDTO, CommentDTO
from datetime import datetime, timezone

class RedditClient:
    def __init__(self, client_id, client_secret, user_agent):
        self._client_id = client_id
        self._client_secret = client_secret
        self._user_agent = user_agent
        self._reddit = None
        self._create_client()
        
    def _create_client(self):
        self._reddit = praw.Reddit(client_id=self._client_id, 
                                   client_secret=self._client_secret,
                                   user_agent=self._user_agent)
        
        
        
class PostFetcher:
    def __init__(self, reddit_client):
        self.reddit_client = reddit_client._reddit
        
    def fetch_posts(self, subreddit_name, search_terms, limit=10):
        subreddit = self.reddit_client.subreddit(subreddit_name)
        return subreddit.search(' OR '.join(search_terms), limit=limit, time_filter="week")
    
    
class CommentProcessor:
    def __init__(self):
        self.filtered_comments = []
        
    def filter_comments(self, posts, search_terms, ticker):
        return [
            self._parse_comment(comment)
            for post in posts
            if self._is_post_relevant(post, search_terms)
            for comment in post.comments.list()
            if self._is_comment_recent(comment) and self._is_comment_relevant(comment, search_terms, ticker)
        ]
    
    def _is_post_relevant(self, post, search_terms):
        return any(term.lower() in post.title.lower() for term in search_terms)
    
    def _is_comment_recent(self, comment):
        return time.time() - comment.created_utc <= 172800
    def _is_comment_relevant(self, comment, search_terms, ticker):
        return any(term.lower() in comment.body.lower() for term in search_terms) and ticker.lower() in comment.body.lower()
    def _parse_comment(self, comment):
        return CommentDTO(
            comment=comment.body,
            score=comment.score,
            timestamp=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
        )
    
    
         
class ScraperAPI:
    def __init__(self, client_id, client_secret, user_agent):
        self._reddit_client = RedditClient(client_id, client_secret, user_agent)
        self._post_fetcher = PostFetcher(self._reddit_client)
        self._comment_processor = CommentProcessor()
        self._results = None
    def get_recent_comments(self, subreddit_name, company_names, ticker, limit=10):
       search_terms = [ticker, *company_names]
       posts = self._post_fetcher.fetch_posts(subreddit_name, search_terms, limit=limit)
       filtered_comments = self._comment_processor.filter_comments(posts, search_terms, ticker)
       self._results = CommentBatchDTO(comments=filtered_comments)
       

       
  
   
    @property
    def filtered_comments(self):return self._results if self._results is not None else CommentBatchDTO()
    
    
  
  
        