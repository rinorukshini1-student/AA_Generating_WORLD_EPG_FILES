import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import json, random, time
from collections import defaultdict

BASE_URL = "https://tvepg.eu"
states = [
    {"id": 1, "name": "United Kingdom", "href": "/en/united_kingdom"},
    {"id": 2, "name": "Ireland", "href": "/en/ireland"},
    {"id": 3, "name": "Germany", "href": "/en/germany"},
    {"id": 4, "name": "France", "href": "/en/france"},
    {"id": 5, "name": "Italy", "href": "/en/italy"},
    {"id": 6, "name": "Spain", "href": "/en/spain"},
    {"id": 7, "name": "Portugal", "href": "/en/portugal"},
    {"id": 8, "name": "Netherlands", "href": "/en/netherlands"},
    {"id": 9, "name": "Belgium", "href": "/en/belgium"},
    {"id": 10, "name": "Austria", "href": "/en/austria"},
    {"id": 11, "name": "Luxembourg", "href": "/en/luxembourg"},
    {"id": 12, "name": "Switzerland", "href": "/en/switzerland"},
    {"id": 13, "name": "Greece", "href": "/en/greece"},
    {"id": 14, "name": "Cyprus", "href": "/en/cyprus"},
    {"id": 15, "name": "Denmark", "href": "/en/denmark"},
    {"id": 16, "name": "Norway", "href": "/en/norway"},
    {"id": 17, "name": "Sweden", "href": "/en/sweden"},
    {"id": 18, "name": "Finland", "href": "/en/finland"},
    {"id": 19, "name": "Estonia", "href": "/en/estonia"},
    {"id": 20, "name": "Latvia", "href": "/en/latvia"},
    {"id": 21, "name": "Lithuania", "href": "/en/lithuania"},
    {"id": 22, "name": "Poland", "href": "/en/poland"},
    {"id": 23, "name": "Czechia", "href": "/en/czechia"},
    {"id": 24, "name": "Slovakia", "href": "/en/slovakia"},
    {"id": 25, "name": "Hungary", "href": "/en/hungary"},
    {"id": 26, "name": "Romania", "href": "/en/romania"},
    {"id": 27, "name": "Bulgaria", "href": "/en/bulgaria"},
    {"id": 28, "name": "Croatia", "href": "/en/croatia"},
    {"id": 29, "name": "Slovenia", "href": "/en/slovenia"},
    {"id": 30, "name": "North Macedonia", "href": "/en/north_macedonia"},
    {"id": 31, "name": "Bosnia and Herzegovina", "href": "/en/bosnia_herzegovina"},
    {"id": 32, "name": "Serbia", "href": "/en/serbia"},
    {"id": 33, "name": "Albania", "href": "/en/albania"},
    {"id": 34, "name": "Ukraine", "href": "/en/ukraine"},
    {"id": 35, "name": "Russia", "href": "/en/russia"},
    {"id": 36, "name": "Turkey", "href": "/en/turkey"}
]


# START_URL = f"{BASE_URL}/en/spain"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
def day_range(offset_days=0):
    day = datetime.now(timezone(timedelta(hours=1))) + timedelta(days=offset_days)  # CET
    start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=timezone(timedelta(hours=1)))
    end = start + timedelta(days=1) - timedelta(seconds=1)
    return int(start.timestamp()), int(end.timestamp())

def unix_to_minutes(ts):
    dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=1)))  # CET
    return dt.hour * 60 + dt.minute

# ------------------ Smart JSON generation ------------------
def generate_time_preferences(epg_data, max_preferences=20, block_size=60):
    time_genre_map = defaultdict(int)
    for channel, ch_data in epg_data.items():
        for show in ch_data.get("shows", []):
            genre = (show.get("genre") or "other").lower().strip()
            start_min = show.get("start_min", 0)
            block_start = (start_min // block_size) * block_size
            time_genre_map[(block_start, genre)] += 1

    prefs = []
    for (block_start, genre), count in sorted(time_genre_map.items()):
        prefs.append({
            "start": block_start,
            "end": block_start + block_size,
            "preferred_genre": genre,
            "bonus": min(100, 20 + count * 10 + random.randint(0, 10))
        })
    prefs = sorted(prefs, key=lambda x: x["bonus"], reverse=True)[:max_preferences]
    prefs.sort(key=lambda x: x["start"])
    return prefs

def generate_priority_blocks(epg_data, block_size=60, top_n=3):
    block_channel_map = defaultdict(list)
    for i, (channel, ch_data) in enumerate(epg_data.items()):
        for show in ch_data.get("shows", []):
            start_min = show.get("start_min", 0)
            block_start = (start_min // block_size) * block_size
            block_channel_map[block_start].append(i)
    blocks = [(start, start + block_size, chs) for start, chs in block_channel_map.items()]
    blocks.sort(key=lambda x: len(x[2]), reverse=True)
    return [
        {"start": s, "end": e, "allowed_channels": chs}
        for s, e, chs in blocks[:top_n]
    ]

def epg_to_smart_json(epg_data):
    all_starts, all_ends = [], []
    for ch_data in epg_data.values():
        for show in ch_data.get("shows", []):
            all_starts.append(show["start_min"])
            all_ends.append(show["end_min"])
    opening_time = min(all_starts) if all_starts else 480
    closing_time = max(all_ends) if all_ends else 1380
    smart_json = {
        "opening_time": opening_time,
        "closing_time": closing_time,
        "min_duration": 30,
        "max_consecutive_genre": 2,
        "channels_count": len(epg_data),
        "switch_penalty": 5,
        "termination_penalty": 10,
        "time_preferences": generate_time_preferences(epg_data),
        "priority_blocks": generate_priority_blocks(epg_data),
        "channels": []
    }

    for i, (channel, ch_data) in enumerate(epg_data.items()):
        programs = []
        for pid, show in enumerate(ch_data.get("shows", []), start=1):
            programs.append({
                "program_id": show["show_title"],
                "start": show["start_min"],
                "end": show["end_min"],
                "genre": show["genre"],
                "score": random.randint(50, 90)
            })
        smart_json["channels"].append({
            "channel_id": i,
            "channel_name": channel,
            "programs": programs
        })
    return smart_json

# ------------------ Scraping functions ------------------
def get_genre_links():
    try:
        response = requests.get(START_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch {START_URL}: {e}")
        return {}

    soup = BeautifulSoup(html, "html.parser")
    genres = {}
    for h4 in soup.select("h4.card-title"):
        link = h4.find("a", href=True)
        if link and "/epg/" in link["href"]:
            genre_name = h4.get_text(strip=True).replace("Genre:", "").split()[0]
            genres[genre_name] = BASE_URL + link["href"]
    if not genres:
        print(f"⚠️ No genres found on {START_URL}")
    return genres

def get_genre_day_links(genre_url):
    try:
        response = requests.get(genre_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch genre page {genre_url}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    day_links = [BASE_URL + a["href"] for a in soup.select(".card-group a[href*='/epg/']")]
    if not day_links:
        print(f"⚠️ No day links found on {genre_url}")
    return day_links

def get_programs_from_day(day_url, genre):
    try:
        response = requests.get(day_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch {day_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # --- Channels (left side)
    channels = []
    for li in soup.select("ul.grid-left-channels li.amr-tvgrid-ceil-left"):
        a_tag = li.find("a", title=True)
        if not a_tag:
            continue
        channels.append(a_tag["title"].strip())

    # --- Program rows (right side)
    rows = soup.select("div.grid-mobile-row")
    programs = []

    # Pair channels with their rows
    for channel, row in zip(channels, rows):
        for link in row.find_all("a", href=True, title=True):
            title_text = link["title"].strip()
            parts = title_text.split(" ", 1)
            if len(parts) != 2:
                continue
            time_str, show = parts
            try:
                for fmt in ["%H:%M", "%I:%M %p", "%H.%M"]:
                    try:
                        dt = datetime.strptime(time_str, fmt)
                        start_min = dt.hour * 60 + dt.minute
                        break
                    except ValueError:
                        continue
                else:
                    continue
            except Exception:
                continue

            programs.append({
                "channel": channel,
                "show_title": show,
                "genre": genre.lower(),
                "start_min": start_min,
                "end_min": start_min + 30,  # default 30 min
                "url": link["href"]
            })

    print(f"✅ {len(programs)} programs parsed from {day_url}")
    return programs

if __name__ == "__main__":
    print(f"Starting scrape at {datetime.now(timezone(timedelta(hours=1))).strftime('%Y-%m-%d %H:%M:%S')} CET")
    print("Select a country:")
for s in states:
    print(f"{s['id']:2d}.{s['name']}")

# --- User selection ---
while True:
    try:
        choice = int(input("\nEnter country number: "))
        selected = next((s for s in states if s["id"] == choice), None)
        if selected:
            START_URL = f"{BASE_URL}{selected['href']}"
            print(f"\n✅ Selected: {selected['name']}")
            print(f"START_URL = {START_URL}")
        else:
            print("❌ Invalid selection. Try again.")
    except ValueError:
        print("⚠️ Please enter a valid number.")

    choiceDays = int(input("\nEnter number of days that you want to get data: "))

    all_genres = get_genre_links()
    print(f"Found {len(all_genres)} genres: {list(all_genres.keys())}")

    for day_offset in range(choiceDays):
        date_str = (datetime.now(timezone(timedelta(hours=1))) + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        from_ts, to_ts = day_range(day_offset)

        print(f"\n📅 Processing day {date_str} ({from_ts} → {to_ts})")

        
        daily_epg = defaultdict(lambda: {"shows": []})

        for genre, genre_url in all_genres.items():
            print(f"\n🟩 Genre: {genre} ({genre_url})")
            day_links = get_genre_day_links(genre_url)
            day_url = next((u for u in day_links if date_str in u), None)
            if not day_url:
                programs = get_programs_from_day(genre_url, genre)
                for p in programs:
                    daily_epg[p["channel"]]["shows"].append(p)
                time.sleep(random.uniform(1.5, 3.5))  
                continue

            programs = get_programs_from_day(day_url, genre)
            for p in programs:
                daily_epg[p["channel"]]["shows"].append(p)
            time.sleep(random.uniform(1.5, 3.5))  

        if not daily_epg:
            print(f"⚠️ No programs fetched for {date_str}")
            continue

        smart_json = epg_to_smart_json(daily_epg)

        filename = f"{selected['name']}_epg_{date_str}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(smart_json, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved {filename}")
    break  # ✅ Exit the selection loop

