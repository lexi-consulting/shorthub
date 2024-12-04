from requests import get
from bs4 import BeautifulSoup
from understat.api.constants.UnderstatConstants import UnderstatConstants
import re
import json

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
    def extract_match_data(html: str) -> tuple[dict, str]:
        """Extract match data from HTML content."""
        json_dict = {}
        try:
            soup = BeautifulSoup(html, "html.parser")
            scripts = soup.find_all("script")
            for script in scripts:
                if "JSON.parse" in script.text:
                    var_name_match = re.search(r"var\s+(\w+)\s*=\s*", script.text)
                    if var_name_match:
                        var_name = var_name_match.group(1)
                        json_data = script.text.split("JSON.parse('")[1].split("')")[0]
                        json_data = json_data.encode("utf8").decode("unicode_escape")
                        
                        # Fix JSON format by replacing single quotes with double quotes
                        json_data = json_data.replace("\'", "\"").replace("'", '"').replace("\\x", "\\u00")
                        if var_name in ["datesData", "teamsData", "playersData"]:
                            json_dict[var_name] = json.loads(json_data)
        except json.JSONDecodeError as e:
            return None, f"Error decoding JSON: {e}"
        except Exception as e:
            return None, str(e)
        
        if not json_dict:
            return {}, "No match data found"
        return json_dict, None
