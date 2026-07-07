"""
Quick Playwright debug test — run this to see what Avtoelon.uz shows.
Run: venv\Scripts\python.exe test_playwright.py
"""
from playwright.sync_api import sync_playwright
import re
import json

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False so you can SEE it
        page = browser.new_page()
        page.set_default_timeout(20000)

        print("=" * 60)
        print("TEST 1: Avtoelon.uz main page")
        print("=" * 60)
        page.goto("https://avtoelon.uz/avto/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # Screenshot
        page.screenshot(path="test_avtoelon_main.png")
        print("Screenshot saved: test_avtoelon_main.png")

        # Total count
        body = page.inner_text("body")
        m = re.search(r'allaqachon\s+([\d\s]+)\s+ta', body)
        if m:
            print(f"Total count found: {m.group(1).strip()}")
        else:
            print("Total count NOT found in body text")

        # Try to find brand counts
        print("\n--- Checking brand links ---")
        for brand in ["Chevrolet", "Daewoo", "BYD", "Kia"]:
            try:
                # Find any element containing brand name and a number
                els = page.locator(f'text={brand}').all()
                for el in els[:3]:
                    try:
                        parent = el.locator('..')
                        parent_text = parent.inner_text(timeout=2000).strip()
                        print(f"  {brand} parent text: {parent_text[:100]}")
                    except Exception:
                        pass
            except Exception as e:
                print(f"  {brand} error: {e}")

        # Get all unique class names
        print("\n--- Page class names ---")
        classes = page.evaluate("""() => {
            const cls = new Set();
            document.querySelectorAll('[class]').forEach(el => {
                (el.className || '').split(' ').forEach(c => {
                    if (c && (c.includes('list') || c.includes('item') || c.includes('elem') || c.includes('card') || c.includes('brand') || c.includes('count'))) {
                        cls.add(c);
                    }
                });
            });
            return Array.from(cls);
        }""")
        print(json.dumps(classes, ensure_ascii=False, indent=2))

        print("\n" + "=" * 60)
        print("TEST 2: Avtoelon.uz Cobalt search")
        print("=" * 60)
        page.goto("https://avtoelon.uz/avto/?search=cobalt", wait_until="networkidle", timeout=25000)
        page.wait_for_timeout(3000)
        page.screenshot(path="test_avtoelon_cobalt.png")
        print("Screenshot saved: test_avtoelon_cobalt.png")

        # Count visible listings
        for sel in ['.a-list-item', '.a-elem', '[class*="list-item"]', '[class*="card"]', 'article']:
            count = page.locator(sel).count()
            if count > 0:
                print(f"  '{sel}' -> {count} items FOUND!")
                # Get first item's full HTML class info
                first = page.locator(sel).first
                first_classes = first.evaluate("el => el.className")
                first_text = first.inner_text()[:200]
                print(f"  First item classes: {first_classes}")
                print(f"  First item text: {first_text}")
            else:
                print(f"  '{sel}' -> 0 items")

        # Also check ALL class names on search results page
        print("\n--- Search page class names ---")
        classes2 = page.evaluate("""() => {
            const cls = new Set();
            document.querySelectorAll('[class]').forEach(el => {
                (el.className || '').split(' ').forEach(c => {
                    if (c && c.length > 2) cls.add(c);
                });
            });
            return Array.from(cls).slice(0, 50);
        }""")
        print(json.dumps(classes2, ensure_ascii=False, indent=2))

        print("\n" + "=" * 60)
        print("TEST 3: Ko'chmas mulk (Nedvizhimost)")
        print("=" * 60)
        page.goto("https://avtoelon.uz/nedvizhimost/", wait_until="networkidle", timeout=25000)
        page.wait_for_timeout(2000)
        page.screenshot(path="test_avtoelon_re.png")

        body = page.inner_text("body")
        m = re.search(r'allaqachon\s+([\d\s]+)\s+ta', body)
        if m:
            print(f"RE total count: {m.group(1).strip()}")

        browser.close()
        print("\nDONE! Check screenshots: test_avtoelon_main.png, test_avtoelon_cobalt.png, test_avtoelon_re.png")

if __name__ == '__main__':
    test()
