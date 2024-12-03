from understat.api.constants.UnderstatConstants import UnderstatConstants
from understat.api.services.UnderstatAPIService import UnderstatAPIService
from understat.api.models.UnderstatHTMLRequest import UnderstatHTMLRequest

class UnderstatService:
    """Service for managing Understat data operations."""

    @classmethod
    def mine_all_match_data(cls) -> tuple[dict, str]:
        """Mine all match data for specified leagues and seasons."""
        all_match_data = {}
        errors = []
        for league in UnderstatConstants.LEAGUES:
            all_match_data[league] = {}
            for season in UnderstatConstants.SEASONS:
                all_match_data[league][season], error = cls.mine_league_season_data(league, season)
                if error:
                    errors.append(error)
        return all_match_data, errors

    @classmethod
    def mine_league_season_data(cls, league: str, season: str) -> tuple[bool, str]:
        """Mine match data for a specific league and season."""
        html, error = UnderstatAPIService.fetch_html(league, season)
        if error:
            return False, error
        
        data, error = UnderstatAPIService.extract_match_data(html)
        if error:
            return False, error
        
        UnderstatHTMLRequest.objects.create(
            url=f"{UnderstatConstants.BASE_URL}{league}/{season}",
            response=html,
            parsed_data=str(data),
            success=True
        )
        
        return True, None
        

