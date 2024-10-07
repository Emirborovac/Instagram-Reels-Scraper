import re
import json

# Function to extract the 720p video URL based on the shortcode
def extract_720p_video_url(file_path, shortcode):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Look for the JSON-like structure that contains the shortcode
        shortcode_pattern = re.compile(r'{"items":\[{"code":"' + re.escape(shortcode) + r'".*?"video_versions":(\[.*?\])')
        shortcode_match = shortcode_pattern.search(html_content)

        if shortcode_match:
            video_versions_json = shortcode_match.group(1)
            video_versions = json.loads(video_versions_json)

            # Loop through video versions to find the 720p version
            for video in video_versions:
                if video.get("width") == 720:
                    video_url = video.get("url").replace("\\u0026", "&")  # Replace the escaped characters
                    print(f"720p Video URL: {video_url}")
                    return video_url

            print("No 720p video URL found.")
        else:
            print(f"No video versions found for shortcode: {shortcode}")

    except Exception as e:
        print(f"Error: {e}")

# Path to the saved HTML file
html_file_path = "C:/Users/Ymir/Desktop/Git Adventure/War Room/DAwmqvDqY6z.html"  # Replace with the actual path
shortcode = "DAwmqvDqY6z"  # Replace with the actual shortcode you want to extract

# Call the function
extract_720p_video_url(html_file_path, shortcode)
