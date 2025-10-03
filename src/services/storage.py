"""In-memory storage for URL mappings"""
from typing import Dict, Optional, List
from datetime import datetime
from collections import defaultdict


class URLStorage:
    """Simple in-memory URL storage with access tracking"""

    def __init__(self):
        self._urls: Dict[str, str] = {}
        self._access_counts: Dict[str, int] = defaultdict(int)
        self._created_at: Dict[str, str] = {}

    def save(self, short_code: str, original_url: str) -> None:
        """Save a URL mapping"""
        self._urls[short_code] = original_url
        self._created_at[short_code] = datetime.now().isoformat()

    def get(self, short_code: str) -> Optional[str]:
        """Retrieve original URL by short code"""
        return self._urls.get(short_code)

    def get_with_details(self, short_code: str) -> Optional[Dict]:
        """Retrieve URL with access count and metadata"""
        if short_code not in self._urls:
            return None
        return {
            "original_url": self._urls[short_code],
            "access_count": self._access_counts[short_code],
            "created_at": self._created_at.get(short_code)
        }

    def increment_access(self, short_code: str) -> None:
        """Increment access count for a short code"""
        if short_code in self._urls:
            self._access_counts[short_code] += 1

    def update(self, short_code: str, new_url: str) -> bool:
        """Update existing URL. Returns True if updated, False if not found"""
        if short_code in self._urls:
            self._urls[short_code] = new_url
            return True
        return False

    def exists(self, short_code: str) -> bool:
        """Check if short code exists"""
        return short_code in self._urls

    def delete(self, short_code: str) -> bool:
        """Delete a URL mapping. Returns True if deleted, False if not found"""
        if short_code in self._urls:
            del self._urls[short_code]
            if short_code in self._access_counts:
                del self._access_counts[short_code]
            if short_code in self._created_at:
                del self._created_at[short_code]
            return True
        return False

    def bulk_delete(self, short_codes: List[str]) -> tuple[int, List[str]]:
        """Delete multiple URLs. Returns (deleted_count, failed_codes)"""
        deleted = 0
        failed = []
        for code in short_codes:
            if self.delete(code):
                deleted += 1
            else:
                failed.append(code)
        return deleted, failed

    def get_all(self) -> Dict[str, str]:
        """Get all URL mappings"""
        return self._urls.copy()

    def get_all_with_stats(self) -> List[Dict]:
        """Get all URLs with access counts"""
        return [
            {
                "short_code": code,
                "original_url": url,
                "access_count": self._access_counts[code],
                "created_at": self._created_at.get(code)
            }
            for code, url in self._urls.items()
        ]

    def search(self, query: str) -> List[Dict]:
        """Search URLs by short code or original URL"""
        query_lower = query.lower()
        results = []
        for code, url in self._urls.items():
            if query_lower in code.lower() or query_lower in url.lower():
                results.append({
                    "short_code": code,
                    "original_url": url,
                    "access_count": self._access_counts[code]
                })
        return results

    def get_stats(self) -> Dict:
        """Get storage statistics"""
        total_accesses = sum(self._access_counts.values())
        sorted_by_access = sorted(
            self._access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        most_accessed = [
            {"short_code": code, "access_count": count}
            for code, count in sorted_by_access[:5]
        ]

        least_accessed = [
            {"short_code": code, "access_count": count}
            for code, count in sorted_by_access[-5:]
        ]

        return {
            "total_urls": len(self._urls),
            "total_accesses": total_accesses,
            "most_accessed": most_accessed,
            "least_accessed": least_accessed
        }

    def count(self) -> int:
        """Get total number of URLs"""
        return len(self._urls)

    def clear(self) -> None:
        """Clear all URLs"""
        self._urls.clear()
        self._access_counts.clear()
        self._created_at.clear()


# Singleton instance
url_storage = URLStorage()
