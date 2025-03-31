import json
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone

def unix_to_normal(unix_time, format="%Y-%m-%d %H:%M:%S"):
    return datetime.fromtimestamp(unix_time, tz=timezone.utc).strftime(format)

# List to store captured responses
responses = {}

def get_selected_attributes(video):
    url = generate_url_new(video)
    selected_data = {
        "nickname": video["author"]["nickname"],
        "userId": video["author"]["id"],
        "privateAccount": video["author"]["privateAccount"],
        "signature": video["author"]["signature"],
        "uniqueId": video["author"]["uniqueId"],
        "verified": video["author"]["verified"],
        "videoId": video["id"],
        "createTime": video["createTime"],
        "likesCount": video["stats"]["diggCount"],
        "shareCount": video["stats"]["shareCount"],
        "commentCount": video["stats"]["commentCount"],
        "playCount": video["stats"]["playCount"],
        "collectCount": video["stats"]["collectCount"],
        "description": video["desc"],
        "url": url,
        "timestamp": unix_to_normal(video["createTime"])
    }

    if "duration" in video["video"]:
        selected_data["duration"] = video["video"]["duration"]
    
    return selected_data

def normalize_response(response):
    videos = {}
    for item in response["itemList"]:
        video = get_selected_attributes(item)
        videos[f"{video["videoId"]}"] = video
    print("videos amount: ", len(videos))
    return videos


def generate_url_new(video):
    url = f"https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["id"]}"
    return url

def capture_response(response):
    # Check if the response URL matches the one you are interested in
    if "https://www.tiktok.com/api/post/item_list/" in response.url:
        # Print and store the response URL and body (if it's JSON)
        try:
            response_data = response.json()
            print("Videos from profile: ", response_data["itemList"][0]["authorStats"]["videoCount"])
            response_data = normalize_response(response_data)
            responses.update(response_data)  # Store the response data
            print(f"Responses size: {len(responses)}")
        except Exception as e:
            print(f"Error parsing response: {e}")
            exit()

def scroll_page(page):
    # Scroll down by a certain amount
    page.evaluate("window.scrollBy(0, window.innerHeight)")
    page.wait_for_timeout(2000)  # Wait for 1 second after scrolling

def scrape(username, max_videos=1000):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            # Listen for responses
            page.on("response", capture_response)

            # Navigate to the page
            page.goto(f"https://www.tiktok.com/@{username}")

            # Wait for the page to load initially
            page.wait_for_load_state("networkidle")

            # Scroll and capture responses multiple times
            while(len(responses) <= max_videos):
                scroll_page(page)
                if (len(responses) >= max_videos):
                    break

        except Exception as e:  # Catch any other exception
            print(f"Some error occurred: {e}")
        finally:
            # save the captured responses to a file
            with open("responses.json", "w", encoding="utf-8") as f:
                json.dump(responses, f, ensure_ascii=False, indent=4)

            # Wait for responses to be captured
            page.wait_for_timeout(2000)  # Wait 2 seconds to capture all responses

            # Print the number of responses captured
            print(f"Captured {len(responses)} responses")

            # Close the browser
            browser.close()

if __name__ == "__main__":
    scrape("gatogalactico", 1000)
