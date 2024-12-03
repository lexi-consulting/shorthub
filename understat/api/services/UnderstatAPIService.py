from requests import get
from bs4 import BeautifulSoup
from json import loads
from understat.api.constants.UnderstatConstants import UnderstatConstants

class UnderstatAPIService:
    """Service for interacting with the Understat API."""

    @staticmethod
    def fetch_html(league: str, season: str) -> tuple[str, str]:
        """Fetch HTML content from Understat."""
        if league not in UnderstatConstants.LEAGUES:
            return None, f"Invalid league: {league}. Must be one of {UnderstatConstants.LEAGUES}"
        if season not in UnderstatConstants.SEASONS:
            return None, f"Invalid season: {season}. Must be one of {UnderstatConstants.SEASONS}"
        
        url = f"{UnderstatConstants.BASE_URL}{league}/{season}"
        try:
            response = get(url)
            return response.text, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def extract_match_data(html: str) -> tuple[list, str]:
        """Extract match data from HTML content."""
        json_array = []
        try:
            soup = BeautifulSoup(html, "html.parser")
            scripts = soup.find_all("script")
            for script in scripts:
                if "JSON.parse" in script.text:
                    json_data = script.text.split("JSON.parse('")[1].split("')")[0]
                    json_data = json_data.encode("utf8").decode("unicode_escape")
                    json_array.append(loads(json_data))
        except Exception as e:
            return None, str(e)
        
        if not json_array:
            return [], "No match data found"
        
        return json_array, None
