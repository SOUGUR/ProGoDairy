import re
from datetime import datetime

def parse_prices_from_markdown(markdown_content):
    """
    Extract milk prices by state from scraped markdown content.
    Parses the markdown table for real data without simulation.
    """
    prices = []
    lines = markdown_content.split('\n')
    in_table = False
    headers = None
    for line in lines:
        line = line.strip()
        if line.startswith('|'):
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if not in_table:
                if len(cells) > 1:
                    headers = [h.replace('**', '').strip() for h in cells]
                    in_table = True
                continue
            if any('---' in cell for cell in cells):
                continue
            if len(cells) >= len(headers):
                data = dict(zip(headers, cells))
                if data.get('Product', '').lower() == 'milk':
                    try:
                        state = data.get('State', '')
                        brand = data.get('Federation/Union', '')
                        variant = data.get('Variant', '')
                        price_str = data.get('CCP (in Rs.)', '0')
                        match = re.match(r'(\d+\.?\d*)', price_str)
                        current_price = float(match.group(1)) if match else 0.0
                        updated_str = data.get('W.E.F', '')
                        updated_at = datetime.strptime(updated_str, '%d-%b-%Y') if updated_str else datetime.now()
                        prices.append({
                            "state": state,
                            "brand": brand,
                            "variant": variant,
                            "current_price": current_price,
                            "updated_at": updated_at
                        })
                    except ValueError:
                        # Skip if parsing fails
                        pass
    return prices

def parse_news_from_markdown(markdown_content):
    """
    Parse dairy-related news articles from Economic Times topic page.
    Handles messy FireCrawl output.
    """
    articles = []
    lines = markdown_content.split('\n')
    dairy_keywords = ['dairy', 'milk', 'cattle', 'buffalo', 'livestock', 'pasteurization',
                     'farmer', 'agriculture', 'cooperative', 'amul', 'mother dairy', 'nddb']

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for: ## [Title](URL)
        title_match = re.match(r'##\s*\[(.+?)\]\((https?://.+?)\)', line)
        if title_match:
            title = title_match.group(1).strip()
            url = title_match.group(2)

            # Check if relevant
            if not any(keyword in title.lower() for keyword in dairy_keywords):
                i += 1
                continue  # Skip non-dairy

            # Extract date from next lines
            published_at = datetime.now()
            excerpt = ""
            for j in range(i+1, min(i+10, len(lines))):
                next_line = lines[j].strip()
                # Match date: "24 Aug, 2025, 11:10 AM IST"
                date_match = re.search(r'(\d{1,2} [A-Za-z]{3}, \d{4}, \d{1,2}:\d{2} [AP]M IST)', next_line)
                if date_match:
                    try:
                        published_at = datetime.strptime(date_match.group(1), '%d %b, %Y, %I:%M %p IST')
                    except ValueError:
                        pass
                    # Use next non-date line as excerpt
                    if j+1 < len(lines):
                        excerpt = lines[j+1].strip()
                        if len(excerpt) > 200:
                            excerpt = excerpt[:200] + "..."
                    break

            articles.append({
                "title": title,
                "url": url,
                "excerpt": excerpt,
                "source": "Economic Times",
                "published_at": published_at
            })

            if len(articles) >= 5:
                break

        i += 1

    return sorted(articles, key=lambda x: x["published_at"], reverse=True)