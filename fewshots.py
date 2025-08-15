import pandas as pd
import json
import os

class FewShotPosts:
    def __init__(self, file_path="data/processed_posts.json"):
        """
        Few-shot examples loader for LinkedIn post generation.
        Reads a processed JSON file of past posts and prepares it for filtering.
        """
        self.df = None
        self.unique_tags = []
        self.load_posts(file_path)

    def load_posts(self, file_path):
        """Load processed posts and prepare DataFrame."""
        if not os.path.exists(file_path):
            print(f"[WARN] {file_path} not found. Few-shot examples disabled.")
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                posts = json.load(f)
        except json.JSONDecodeError:
            print(f"[ERROR] Could not parse {file_path}")
            return

        if not posts:
            print("[WARN] No posts found in processed_posts.json")
            return

        self.df = pd.json_normalize(posts)

        if 'line_count' in self.df.columns:
            self.df['length'] = self.df['line_count'].apply(self.categorize_length)

        if 'tags' in self.df.columns:
            all_tags = sum(self.df['tags'], [])
            self.unique_tags = sorted(set(all_tags))

    def get_filtered_posts(self, length, language, tag):
        """
        Return at most two few-shot examples matching length, language, and tag.
        If none match, return empty list.
        """
        if self.df is None or self.df.empty:
            return []

        tag_lower = tag.lower()
        df_filtered = self.df[
            (self.df['tags'].apply(lambda tags: any(t.lower() == tag_lower for t in tags))) &
            (self.df['language'].str.lower() == language.lower()) &
            (self.df['length'] == length)
        ]

        return df_filtered.head(2).to_dict(orient='records')  # limit to 2 examples

    def categorize_length(self, line_count):
        """Categorize posts into Short, Medium, Long."""
        if line_count < 5:
            return "Short"
        elif 5 <= line_count <= 10:
            return "Medium"
        return "Long"

    def get_tags(self):
        """Return all unique tags found in dataset."""
        return self.unique_tags


if __name__ == "__main__":
    fs = FewShotPosts()
    examples = fs.get_filtered_posts("Medium", "English", "Job Search")
    print(examples)
