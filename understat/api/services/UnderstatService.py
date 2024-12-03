from understat.api.constants.UnderstatConstants import UnderstatConstants
from understat.api.services.UnderstatAPIService import UnderstatAPIService
from understat.api.models.HTMLRequest import HTMLRequest

class UnderstatService:
    """Service for managing Understat data operations."""

    @classmethod
    def mine_all_match_data(cls) -> tuple[bool, list[str]]:
        """Mine all match data for specified leagues and seasons."""
        all_match_data = {}
        errors = []
        for league in UnderstatConstants.LEAGUES:
            all_match_data[league] = {}
            for season in UnderstatConstants.SEASONS:
                success, error = cls.mine_league_season_data(league, season)
                if error:
                    errors.append(error)
        if errors:
            return False, errors
        return True, None

    @classmethod
    def mine_league_season_data(cls, league: str, season: str) -> tuple[bool, str]:
        """Mine match data for a specific league and season."""
        html, error = UnderstatAPIService.fetch_html(league, season)
        if error:
            return False, error
        
        data, error = UnderstatAPIService.extract_match_data(html)
        if error:
            return False, error
        
        try:
            HTMLRequest.objects.create(
                url=f"{UnderstatConstants.BASE_URL}{league}/{season}",
                response=html,
                parsed_data=str(data),
                success=True
            )
            return True, None
        except Exception as e:
            return False, str(e)