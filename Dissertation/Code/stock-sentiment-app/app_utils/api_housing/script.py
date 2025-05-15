from .scraper_api import ScraperAPI
import praw

if __name__ == "__main__":
    scraper = ScraperAPI("RRyDC9aJ-EHivs_Q6nDOoA", 	"I-gumhH5W60wITJ8ZsnyYkpUIiuifg",  "Extreme_Radish1654")
    scraper.get_recent_comments(["stocks"],["Tesla", "Elon"] , "TSLA")
    print(scraper.filtered_comments)
    
      