import requests
import json

# The URL for LeetCode's GraphQL API endpoint
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

# The GraphQL query to fetch recent submissions.
# We only need the question title and the submission status.
# NOTE: Changed "question { title }" to just "title" based on recent API changes.
SUBMISSIONS_QUERY = """
query recentSubmissionList($username: String!, $limit: Int!) {
  recentSubmissionList(username: $username, limit: $limit) {
    statusDisplay
    title
  }
}
"""

def get_latest_submissions(username: str, limit: int = 15):
    """
    Fetches the latest code submissions for a given LeetCode user.

    Args:
        username: The LeetCode username to look up.
        limit: The number of recent submissions to fetch and check.

    Returns:
        A list of submission dictionaries, or None if the request fails
        or the user is not found.
    """
    print(f"Checking the last {limit} submissions for user '{username}'...")
    
    # Define the payload for the POST request
    payload = {
        "query": SUBMISSIONS_QUERY,
        "variables": {
            "username": username,
            "limit": limit
        }
    }
    
    # Set headers to mimic a browser request
    headers = {
        'Content-Type': 'application/json',
        'Referer': f'https://leetcode.com/{username}/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    
    try:
        # Make the POST request to the GraphQL API
        response = requests.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors in the GraphQL response (e.g., user not found)
            if 'errors' in data:
                print(f"Error: {data['errors'][0]['message']}")
                return None
            
            # Extract the submission data using the updated field name
            submissions = data.get('data', {}).get('recentSubmissionList')
            return submissions
        else:
            # Provide more details on failure, including the response body if available
            print(f"Error: Failed to fetch data. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return None

def display_solved_questions(submissions, username, limit):
    """
    Filters for 'Accepted' submissions and displays the unique question titles.

    Args:
        submissions: A list of submission dictionaries.
        username: The LeetCode username, for display purposes.
        limit: The number of submissions that were checked.
    """
    if not submissions:
        print(f"Could not find any recent submissions for user '{username}'.")
        return

    # Use a set to store unique question titles to avoid duplicates
    solved_questions = set()

    for sub in submissions:
        # Check if the submission status is 'Accepted' using the new 'statusDisplay' field
        if sub.get('statusDisplay') == 'Accepted':
            # Add the question title to our set, accessed directly from the submission object
            title = sub.get('title')
            if title:
                solved_questions.add(title)
    
    if not solved_questions:
        print(f"No successfully solved questions found in the last {limit} submission(s) for '{username}'.")
    else:
        print(f"\n--- Recently Solved Questions by {username} ---")
        # Convert set to list to print with numbers
        solved_list = list(solved_questions)
        return solved_list

# if __name__ == "__main__":
#     try:
#         leetcode_username = input("Enter LeetCode username: ")
#         num_to_check_str = input("How many recent submissions to check? (default: 15): ")
        
#         # Use default value if input is empty, otherwise convert to integer
#         num_to_check = int(num_to_check_str) if num_to_check_str else 15
#         st=time.time()
#         if leetcode_username:
#             latest_submissions = get_latest_submissions(leetcode_username, num_to_check)
#             if latest_submissions is not None:
#                 display_solved_questions(latest_submissions, leetcode_username, num_to_check)
#         else:
#             print("Username cannot be empty.")
#         en=time.time()
#         print(en-st)
#     except ValueError:
#         print("Invalid number. Please enter an integer.")
#     except KeyboardInterrupt:
#         print("\nOperation cancelled by user.")

