from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
@dataclass
class CommentDTO:
    comment:str
    score: int
    timestamp:datetime
    date : datetime.date = field(init=False)
    
    def __post_init__(self):
        if isinstance(self.timestamp, (float, int)):
            self.timestamp = datetime.fromtimestamp(self.timestamp)
        self.date = self.timestamp.date()
    def format_comment(self)->str:
        return f"Comment: {self.comment}, Score:{self.score}, Date: {self.date} Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{'-' * 50}"

@dataclass
class CommentBatchDTO:
    comments:list[CommentDTO] = field(default_factory=list)
    
    def add_comment(self, comment:CommentDTO):
        self.comments.append(comment)
    def get_comments(self)->list[CommentDTO]:return self.comments
    
    def get_comments_as_strings(self)->list[str]:return [comment.format_comment() for comment in self.comments]
    def to_pandas(self)-> pd.DataFrame:return pd.DataFrame([{
        "comment": c.comment,
        "score": c.score,
        "timestamp": c.timestamp,
        "date": c.date
        } for c in self.comments])