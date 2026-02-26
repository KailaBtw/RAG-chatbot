import json
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Prefer local import so this script can run directly from its folder
try:
    from wiki_api import MediaWikiClient  # type: ignore
except Exception:  # pragma: no cover - fallbacks for package/module runs
    try:
        from .wiki_api import MediaWikiClient  # type: ignore
    except Exception:
        from Applications.Genre_Analysis.wiki_api import MediaWikiClient  # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500, help="Number of titles to fetch (max 500)")
    parser.add_argument(
        "--user-agent",
        type=str,
        default="GenreAnalysisBot/0.1 (contact: ellielagrave@gmail.com)",
        help="Custom User-Agent string",
    )
    args = parser.parse_args()

    client = MediaWikiClient(user_agent=args.user_agent)

    # Load existing data to avoid duplicates
    out_dir = Path(__file__).parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "runescape_top100.json"
    
    existing_pages = []
    existing_titles = set()
    
    if out_path.exists():
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                existing_pages = json.load(f)
                existing_titles = {page.get('title', '') for page in existing_pages}
            print(f"[genre-analysis] Loaded {len(existing_pages)} existing pages from cache")
        except Exception as e:
            print(f"[genre-analysis] Error loading existing data: {e}")
            existing_pages = []
            existing_titles = set()

    print(f"[genre-analysis] Fetching {args.limit} random titles...")
    titles = client.get_random_titles_batch(total_limit=args.limit, batch_size=500)
    print(f"[genre-analysis] Retrieved {len(titles)} unique titles")

    # Filter out titles we already have
    new_titles = [title for title in titles if title not in existing_titles]
    print(f"[genre-analysis] {len(new_titles)} new titles to process")

    def fetch_page(title):
        """Fetch a single page's wikitext with retry logic and rate limiting."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                wikitext = client.get_page_wikitext(title)
                return {
                    "title": title,
                    "wikitext": wikitext,
                }
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    # Rate limited - wait longer before retry
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    print(f"[genre-analysis] Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                elif attempt == max_retries - 1:
                    print(f"[genre-analysis] Failed to fetch {title} after {max_retries} attempts: {e}")
                    return None
                else:
                    time.sleep(2)  # Wait before retry for other errors
        return None

    new_pages = []
    print(f"[genre-analysis] Processing {len(new_titles)} pages in parallel...")
    
    # Use ThreadPoolExecutor for parallel processing (reduced workers to avoid rate limits)
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_title = {executor.submit(fetch_page, title): title for title in new_titles}
        
        # Process completed tasks
        completed = 0
        failed = 0
        for future in as_completed(future_to_title):
            title = future_to_title[future]
            try:
                page_data = future.result()
                if page_data:
                    new_pages.append(page_data)
                else:
                    failed += 1
                completed += 1
                if completed % 100 == 0:  # Progress update every 100 pages
                    print(f"[genre-analysis] Processed {completed}/{len(new_titles)} pages... ({failed} failed)")
            except Exception as e:
                print(f"[genre-analysis] Error processing {title}: {e}")
                failed += 1
                completed += 1
    
    print(f"[genre-analysis] Completed processing {len(new_pages)} new pages ({failed} failed)")

    # Combine existing and new pages
    all_pages = existing_pages + new_pages
    client.write_json(str(out_path), all_pages)
    print(f"[genre-analysis] Wrote {len(all_pages)} total pages to {out_path} ({len(new_pages)} new)")


if __name__ == "__main__":
    main()


