import re
import json
import datetime
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    text = text.replace("\u200e", "")  # remove left-to-right marker if any
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_summary(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    return clean_text(text.replace("\n", " ").replace("。", "."))


def clean_review_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = clean_text(text)
    text = re.sub(r"[^\w\s,.!?]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) > 10 else ""


def format_place_structured(place: dict) -> dict:
    def safe_get(path, default=""):
        keys = path.split(".")
        val = place
        for key in keys:
            val = val.get(key, {})
        return val if isinstance(val, str) else default

    name = clean_text(safe_get("displayName.text", "Unknown"))
    types = place.get("types", [])
    tags = ", ".join(types)
    summary = clean_summary(safe_get("editorialSummary.text"))
    rating = place.get("rating", None)
    reviews_count = place.get("userRatingCount", None)
    google_rating = (
        f"{rating} ({reviews_count} reviews)" if rating and reviews_count else "N/A"
    )
    maps_link = place.get("googleMapsUri", "")
    services = [
        key
        for key in [
            "takeout",
            "delivery",
            "dineIn",
            "reservable",
            "servesLunch",
            "servesDinner",
            "servesVegetarianFood",
        ]
        if place.get(key)
    ]
    audience = [
        key
        for key in ["goodForChildren", "goodForGroups", "goodForWatchingSports"]
        if place.get(key)
    ]
    open_now = place.get("currentOpeningHours", {}).get("openNow", None)
    open_status = "Currently open" if open_now else "Currently closed"
    weekday = datetime.datetime.today().weekday()
    weekday_descs = place.get("currentOpeningHours", {}).get("weekdayDescriptions", [])
    today_hours = (
        clean_text(weekday_descs[weekday]) if weekday < len(weekday_descs) else "N/A"
    )

    reviews_raw = [
        r.get("text", {}).get("text", "") for r in place.get("reviews", [])[:2]
    ]
    reviews = [clean_review_text(r) for r in reviews_raw if clean_review_text(r)]

    return {
        "name": name,
        "google_rating": google_rating,
        "tags": tags,
        "services": services,
        "audience": audience,
        "status": open_status,
        "today_hours": today_hours,
        "map": maps_link,
        "summary": summary,
        "reviews": reviews,
    }


def build_prompt_template(lang="en"):
    instruction_en = """
You are a helpful food recommender.
The user is looking for: "{query}"

Each entry contains a place's name, services, suitable audience (e.g., for groups), summary, and a few reviews.
Ignore Google rating numbers when deciding.

Select the top 5 places that best match the user's intent. Return a JSON array. For each:
- name
- reason (why it's a good match)
- score (relevance 1–10)

Only return a valid JSON array.

Restaurant list:
{places_text}
"""

    instruction_zh = """
你是一位有幫助的在地美食推薦助手。
使用者正在尋找:「{query}」

以下是幾家餐廳的資訊，包括名稱、服務、適合對象（例如：團體聚餐）、摘要與評論。
請忽略 Google 評分數值，僅依據文字資料推薦。

選出最適合的5家，回傳 JSON 陣列。每筆資料包含：
- name
- reason（推薦原因）
- score（推薦程度 1–10）

僅回傳 JSON 陣列。

店家列表：
{places_text}
"""

    template = instruction_en if lang == "en" else instruction_zh
    return ChatPromptTemplate.from_template(template)


def extract_rating(rating_str: str) -> float:
    if not isinstance(rating_str, str):
        return 0.0
    match = re.search(r"\d+(\.\d+)?", rating_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            pass
    return 0.0


def recommend_from_raw_places(query: str, places: List[Dict], lang="en") -> List[Dict]:
    formatted = [format_place_structured(p) for p in places[:20]]
    text_blocks = []
    for p in formatted:
        block = f"""
Name: {p['name']}
Tags: {p['tags']}
Services: {', '.join(p['services'])}
Suitable For: {', '.join(p['audience'])}
Status: {p['status']}
Today's Hours: {p['today_hours']}
Map: {p['map']}
Summary: {p['summary']}
Reviews:
""" + "\n".join(
            [f"- {r}" for r in p["reviews"]]
        )
        text_blocks.append(block.strip())

    combined = "\n\n---\n\n".join(text_blocks)
    prompt = build_prompt_template(lang=lang)
    chain = prompt | ChatOpenAI(temperature=0.3) | StrOutputParser()

    result_text = chain.invoke({"query": query, "places_text": combined}).strip()
    if result_text.startswith("```json"):
        result_text = result_text.replace("```json", "").strip()
    if result_text.endswith("```"):
        result_text = result_text[:-3].strip()

    try:
        result = json.loads(result_text)
        enriched_results = []
        for match in result:
            matched_place = next(
                (p for p in formatted if p["name"] == match.get("name")), None
            )
            if matched_place:
                enriched_results.append(
                    {
                        **matched_place,
                        "reason": match.get("reason", ""),
                        "gpt_score": match.get("score", 0),
                    }
                )

        sorted_results = sorted(
            enriched_results,
            key=lambda x: (
                x.get("gpt_score", 0),
                extract_rating(x.get("google_rating", "")),
            ),
            reverse=True,
        )

        return sorted_results
    except Exception as e:
        return [{"error": f"Failed to parse GPT output: {str(e)}", "raw": result_text}]
