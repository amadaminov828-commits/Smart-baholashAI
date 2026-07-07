import requests
import sys

def test_redirect(valuation_id):
    # Try the local IP if possible, but for the script localhost is fine to test the route
    url = f"http://localhost:8000/api/v1/vehicles/valuations/{valuation_id}/qr-pdf/"
    print(f"Testing URL: {url}")
    try:
        # Don't follow redirects so we can see the 302
        response = requests.get(url, allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 302:
            print(f"Redirect Location: {response.headers.get('Location')}")
        elif response.status_code == 404:
            print("Error: 404 Not Found. Route might be still incorrect.")
        else:
            print(f"Unexpected status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else "1"
    test_redirect(vid)
