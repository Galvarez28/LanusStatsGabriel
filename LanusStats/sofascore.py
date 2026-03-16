import json
from datetime import datetime
import time
from .functions import get_possible_leagues_for_page, pd, uc, get_random_rate_sleep
from .exceptions import InvalidStrType, MatchDoesntHaveInfo, PlayerDoesntHaveInfo
from faker import Faker
from faker.providers import user_agent
from bs4 import BeautifulSoup

fake = Faker()
fake.add_provider(user_agent)

user_agent_provider = fake.user_agent

class SofaScore:
    
    def __init__(self):
        self.league_stats_fields = [
            'goals',
            'yellowCards',
            'redCards',
            'groundDuelsWon',
            'groundDuelsWonPercentage',
            'aerialDuelsWon',
            'aerialDuelsWonPercentage',
            'successfulDribbles',
            'successfulDribblesPercentage',
            'tackles',
            'assists',
            'accuratePassesPercentage',
            'totalDuelsWon',
            'totalDuelsWonPercentage',
            'minutesPlayed',
            'wasFouled',
            'fouls',
            'dispossessed',
            'possesionLost',
            'appearances',
            'started',
            'saves',
            'totalSaves',
            'savedShots',
            'savesFromInsideBox',
            'savesFromOutsideBox',
            'cleanSheets',
            'savedShotsFromInsideTheBox',
            'savedShotsFromOutsideTheBox',
            'goalsConcededInsideTheBox',
            'goalsConcededOutsideTheBox',
            'highClaims',
            'successfulRunsOut',
            'punches',
            'runsOut',
            'accurateFinalThirdPasses',
            'bigChancesCreated',
            'accuratePasses',
            'keyPasses',
            'accurateCrosses',
            'accurateCrossesPercentage',
            'accurateLongBalls',
            'accurateLongBallsPercentage',
            'interceptions',
            'clearances',
            'dribbledPast',
            'bigChancesMissed',
            'totalShots',
            'shotsOnTarget',
            'blockedShots',
            'goalConversionPercentage',
            'hitWoodwork',
            'offsides',
            'expectedGoals',
            'errorLeadToGoal',
            'errorLeadToShot',
            'passToAssist'
            ]
        self.base_url = 'https://www.sofascore.com/'

    def get_match_id(self, match_url):
        """Get match id for any match.

        Args:
            match_url (string): Full link to a SofaScore match
        Returns:
            string: Match id for a SofaScore match. Used in Urls
        """
        if type(match_url) != str:
            raise InvalidStrType(match_url)
        
        match_id = match_url.split(':')[-1]
        return match_id
        
    def sofascore_request(self, path):
        """Request used to SofaScore.

        Args:
            path (str): Part of the url to make the request

        Returns:
            data: JSON response from SofaScore
        """
        path = f"{self.base_url}{path}"
        fake = Faker()
        user_agent = fake.chrome()

        def make_driver():
            opts = uc.ChromeOptions()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1920,1080")
            opts.add_argument(f"user-agent={user_agent}")
            return opts

        try:
            driver = uc.Chrome(options=make_driver(), version_main=145)
        except Exception:
            try:
                driver = uc.Chrome(options=make_driver())
            except Exception:
                driver = uc.Chrome(options=make_driver())

        try:
            driver.get(path)
            time.sleep(3)
            html = driver.page_source
        finally:
            driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        data = json.loads(soup.text)
        time.sleep(get_random_rate_sleep(1.5, 4))
        return data

    def get_match_data(self, match_url):
        """Gets all the general data from a match.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            json: Data of the match.
        """
        match_id = self.get_match_id(match_url)
        url = f'api/v1/event/{match_id}'
        data = self.sofascore_request(url)
        time.sleep(get_random_rate_sleep(2, 3))
        return data

    def get_match_momentum(self, match_url):
        """Get values of the momentum graph in SofaScore UI.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            DataFrame: Values needed to make a heatmap with pitch.kdeplot.
        """
        match_id = self.get_match_id(match_url)
        url = f'api/v1/event/{match_id}/graph'
        data = self.sofascore_request(url)

        try:
            points = data['graphPoints']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
        match_momentum = pd.DataFrame(points)
        return match_momentum

    def get_match_shotmap(self, match_url, save_csv=False):
        """Get a DataFrame with data of the shots of a match.

        Args:
            match_url (str): Full link to a SofaScore match
            save_csv (bool, optional): Save the DataFrame to a csv. Defaults to False.

        Returns:
            DataFrame: Dataframe with all the data from the shotmap shown in SofaScore UI
        """
        match_id = self.get_match_id(match_url)
        url = f'api/v1/event/{match_id}/shotmap'
        data = self.sofascore_request(url)

        try:
            shots = data['shotmap']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
        match_shots = pd.DataFrame(shots)
        today = datetime.now().strftime('%Y-%m-%d')
        if save_csv:
            match_shots.to_csv(f'shots match - {match_id} - {today}.csv')
        players = match_shots.player.apply(pd.Series)
        coordenates = match_shots.playerCoordinates.apply(pd.Series)
        match_shots = pd.concat([match_shots.drop(columns=['player']), players], axis=1)
        match_shots = pd.concat([match_shots.drop(columns=['playerCoordinates']), coordenates], axis=1)
        return match_shots
    
    def get_positions(self, selected_positions):
        """Returns a string for the parameter filters of the scrape_league_stats() request.

        Args:
            selected_positions (list): List of the positions available to filter on the SofaScore UI

        Returns:
            dict: Goalies, Defenders, Midfielders and Forwards and their translation for the parameter of the request
        """
        positions = {
            'Goalkeepers': 'G',
            'Defenders': 'D',
            'Midfielders': 'M',
            'Forwards': 'F'
        }
        abbreviations = [positions[position] for position in selected_positions]
        return '~'.join(abbreviations)
    
    def scrape_league_stats(self, league, season, save_csv=False, accumulation='total', selected_positions=['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']):
        """Get every player statistic that can be asked in league pages on SofaScore.

        Args:
            league (str): Possible leagues in get_available_leagues("Sofascore")
            season (str): Possible season in get_available_season_for_leagues("Sofascore", league)
            accumulation (str, optional): Value of the filter accumulation. Can be "per90" and "perMatch". Defaults to 'total'.
            selected_positions (list, optional): Value of the filter positions. Defaults to all positions.

        Returns:
            DataFrame: DataFrame with each row corresponding to a player and the columns are the fields defined on get_league_stats_fields()
        """
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        positions = self.get_positions(selected_positions)
        concatenated_fields = "%2C".join(self.league_stats_fields)
        
        offset = 0
        df = pd.DataFrame()
        for i in range(0, 20):
            request_url = (
                f'api/v1/unique-tournament/{league_id}/season/{season_id}/statistics'
                f'?limit=100&order=-rating&offset={offset}'
                f'&accumulation={accumulation}'
                f'&fields={concatenated_fields}'
                f'&filters=position.in.{positions}'
            )
            data = self.sofascore_request(request_url)
            new_df = pd.DataFrame(data['results'])
            player_series = new_df.player.apply(pd.Series)
            team_series = new_df.team.apply(pd.Series)
            new_df['player'] = player_series['name']
            new_df['player_id'] = player_series['id']
            new_df['team'] = team_series['name']
            new_df['team_id'] = team_series['id']
            df = pd.concat([df, new_df])
            
            if data.get('page') == data.get('pages'):
                print('End of the pages')
                break
            offset += 100
            
        if save_csv:
            df.to_csv(f'{league} {season} stats.csv')
            
        if not df.empty:
            if 'totalSaves' in df.columns and 'saves' not in df.columns:
                df['saves'] = df['totalSaves']
            elif 'savedShots' in df.columns and 'saves' not in df.columns:
                df['saves'] = df['savedShots']
            if 'accuratePasses' in df.columns and 'accuratePassesPercentage' in df.columns:
                df['attemptedPasses'] = df.apply(
                    lambda row: round(row['accuratePasses'] / (row['accuratePassesPercentage'] / 100))
                    if pd.notnull(row.get('accuratePassesPercentage')) and row.get('accuratePassesPercentage') > 0 else (row.get('accuratePasses', 0)), axis=1
                )
            if 'successfulDribbles' in df.columns and 'successfulDribblesPercentage' in df.columns:
                df['attemptedDribbles'] = df.apply(
                    lambda row: round(row['successfulDribbles'] / (row['successfulDribblesPercentage'] / 100))
                    if pd.notnull(row.get('successfulDribblesPercentage')) and row.get('successfulDribblesPercentage') > 0 else (row.get('successfulDribbles', 0)), axis=1
                )
        return df
    
    def get_players_match_stats(self, match_url):
        """Returns match data for each player.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            DataFrames: A DataFrame for home and away teams with each row being 
                a player and in each columns a different statistic or data of the player
        """
        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)
        request_url = f'api/v1/event/{match_id}/lineups'
        response = self.sofascore_request(request_url)
        
        names = {'home': home_name, 'away': away_name}
        dataframes = {}
        for team in names.keys():
            data = pd.DataFrame(response[team]['players'])
            try:
                columns_list = [
                    data['player'].apply(pd.Series), data['shirtNumber'], 
                    data['jerseyNumber'], data['position'], data['substitute'],
                    data['statistics'].apply(pd.Series, dtype=object),
                    data['captain']
                ]
            except KeyError:
                raise MatchDoesntHaveInfo(match_url)
            df = pd.concat(columns_list, axis=1)
            df['team'] = names[team]
            dataframes[team] = df
        
        return dataframes['home'], dataframes['away']
    
    def get_team_names(self, match_url):
        """Get the team names for the home and away teams.

        Args:
            match_url (string): Full link to a SofaScore match

        Returns:
            strings: Name of home and away team.
        """
        data = self.get_match_data(match_url)
        try:
            home_team = data['event']['homeTeam']['name']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        away_team = data['event']['awayTeam']['name']
        return home_team, away_team
    
    def get_players_average_positions(self, match_url):
        """Return player averages positions for each team.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            list of DataFrames: Each row is a player and columns averageX and averageY 
                denote their average position on the match.
        """
        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)
        request_url = f'api/v1/event/{match_id}/average-positions'
        data = self.sofascore_request(request_url)
        response = data
        
        names = {'home': home_name, 'away': away_name}
        dataframes = {}
        for team in names.keys():
            data = pd.DataFrame(response[team])
            df = pd.concat(
                [data['player'].apply(pd.Series), data.drop(columns=['player'])],
                axis=1
            )
            df['team'] = names[team]
            dataframes[team] = df
        return dataframes['home'], dataframes['away']

    def get_team_last_matches(self, team_id, n=5):
        """Get the last n matches for a team.

        Args:
            team_id (int|str): Sofascore team ID.
            n (int, optional): Number of matches to return. Defaults to 5.

        Returns:
            list: List of dictionaries with match data.
        """
        request_url = f'api/v1/team/{team_id}/events/last/0'
        data = self.sofascore_request(request_url)
        events = data.get('events', [])
        return events[:n]

    def get_match_h2h(self, match_url):
        """Get H2H history between two teams for a given match.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            list: List of dictionaries with H2H match data.
        """
        match_id = self.get_match_id(match_url)
        request_url = f'api/v1/event/{match_id}/h2h/events'
        try:
            data = self.sofascore_request(request_url)
            return data.get('events', [])
        except Exception as e:
            print(f"Error fetching H2H for match {match_id}: {e}")
            return []
    
    def get_lineups(self, match_url):
        """Get lineups for a match.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            dict: Lineup data for home and away teams.
        """
        match_id = self.get_match_id(match_url)
        request_url = f'api/v1/event/{match_id}/lineups'
        data = self.sofascore_request(request_url)
        return data
    
    def get_player_ids(self, match_url):
        """Get the player ids for a Sofascore match.

        Args:
            match_url (string): Full link to a SofaScore match

        Returns:
            dict: Name and ids of every player in the match
                Key: Name
                Value: Id
        """
        response = self.get_lineups(match_url)
        teams = ['home', 'away']
        player_ids = {}
        for team in teams:
            data = response[team]['players']
            for item in data:
                player_data = item['player']
                player_ids[player_data['name']] = player_data['id']
        return player_ids
    
    def get_player_heatmap(self, match_url, player):
        """Get the x-y coordinates to create a player heatmap. Use Seaborn
        kdeplot() to create the heatmap image.

        Args:
            match_url (str): Full link to a SofaScore match
            player (str): Name of the player (must be the SofaScore one). Use
                Sofascore.get_player_ids()

        Returns:
            DataFrame: Pandas dataframe with x-y coordinates for the player
        """
        match_id = self.get_match_id(match_url)
        player_ids = self.get_player_ids(match_url)
        player_id = player_ids[player]
        request_url = f'api/v1/event/{match_id}/player/{player_id}/heatmap'
        data = self.sofascore_request(request_url)
        
        try:
            heatmap = pd.DataFrame(data['heatmap'])
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        return heatmap
    
    def get_player_match_events(self, match_url, player, events=None):
        """Get the x-y coordinates for a player events.

        Args:
            match_url (str): Full link to a SofaScore match
            player (str): Name of the player (must be the SofaScore one). Use
                Sofascore.get_player_ids()
            events (list|str, optional): 
                - None: Gets passes, ball-carries, dribbles, defensive.
                - all: Gets all available categories in the JSON.
                - list: A specific list e.g. passes, dribbles.

        Returns:
            DataFrame: Pandas dataframe with x-y coordinates for the player
        """
        match_id = self.get_match_id(match_url)
        player_ids = self.get_player_ids(match_url)
        player_id = player_ids[player]
        request_url = f'api/v1/event/{match_id}/player/{player_id}/rating-breakdown'
        data = self.sofascore_request(request_url)

        if 'error' in data:
            raise MatchDoesntHaveInfo(match_url)

        if events is None:
            categories = [k for k in ['passes', 'ball-carries', 'dribbles', 'defensive'] if k in data]
        elif events == 'all':
            categories = [k for k, v in data.items() if isinstance(v, list)]
        else:
            categories = [k for k in events if k in data]

        if not categories:
            return pd.DataFrame()

        df_player_events = pd.concat(
            [pd.json_normalize(data[k]).assign(category=k) for k in categories], 
            ignore_index=True
        )
        df_player_events.rename(columns={
            'playerCoordinates.x': 'x',
            'playerCoordinates.y': 'y',
            'passEndCoordinates.x': 'end_x',
            'passEndCoordinates.y': 'end_y'
        }, inplace=True)

        cols = ['category'] + [c for c in df_player_events.columns if c != 'category']
        df_player_events = df_player_events[cols]
        return df_player_events

    def get_player_season_heatmap(self, league, season, player_id):
        """Get a player season heatmap as shown in the player page in SofaScore UI.

        Args:
            league (str): League name
            season (str): Season name
            player_id (int): SofaScore player ID

        Returns:
            DataFrame: Heatmap points for the player
        """
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        request_url = f'api/v1/player/{player_id}/unique-tournament/{league_id}/season/{season_id}/heatmap/overall'
        data = self.sofascore_request(request_url)
        
        try:
            season_heatmap = pd.DataFrame(data['points'])
        except KeyError:
            raise PlayerDoesntHaveInfo(player_id)
        return season_heatmap

    def get_player_match_history(self, player_id, tournament_id, season_id, n=10):
        """Get the last n matches stats for a specific player in a season."""
        url = f'api/v1/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/events'
        data = self.sofascore_request(url)
        events = data.get('events', [])
        history = []
        for event in events[:n]:
            event_id = event['id']
            stats_url = f'api/v1/event/{event_id}/player/{player_id}/statistics'
            try:
                stats_data = self.sofascore_request(stats_url)
                if 'statistics' in stats_data:
                    history.append({
                        'match_id': event_id,
                        'match_slug': event.get('slug'),
                        'timestamp': event.get('startTimestamp'),
                        'statistics': stats_data.get('statistics', {})
                    })
            except:
                continue
        return history

    def get_player_season_stats_overall(self, player_id, tournament_id, season_id):
        """Get the average stats for a player for the whole season."""
        url = f'api/v1/player/{player_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall'
        data = self.sofascore_request(url)
        return data.get('statistics', {})

    def search_player(self, name):
        """Search for a player by name to get their ID and details."""
        import urllib.parse
        encoded_name = urllib.parse.quote(name)
        url = f'api/v1/search/all?q={encoded_name}'
        data = self.sofascore_request(url)
        players = [r for r in data.get('results', []) if r.get('type') == 'player']
        if not players:
            return None
        return players[0]['entity']

    def search_team(self, name):
        """Search for a team by name to get their ID and details."""
        import urllib.parse
        encoded_name = urllib.parse.quote(name)
        url = f'api/v1/search/all?q={encoded_name}'
        data = self.sofascore_request(url)
        teams = [r for r in data.get('results', []) if r.get('type') == 'team']
        if not teams:
            return None
        return teams[0]['entity']

    def get_current_season_id(self, tournament_id):
        """Get the current season ID for a given tournament."""
        url = f'api/v1/unique-tournament/{tournament_id}/seasons'
        data = self.sofascore_request(url)
        seasons = data.get('seasons', [])
        if not seasons:
            return None
        return seasons[0]['id']

    def get_player_h2h_history(self, player_id, team_id, opponent_team_id, n=5):
        """Get the last N matches a player played against an opponent team."""
        events = []
        for page in range(4):
            url = f'api/v1/team/{team_id}/events/last/{page}'
            try:
                data = self.sofascore_request(url)
                page_events = data.get('events', [])
                if not page_events:
                    break
                events.extend(page_events)
            except Exception:
                break

        h2h_events = []
        for event in events:
            home_id = event.get('homeTeam', {}).get('id')
            away_id = event.get('awayTeam', {}).get('id')
            if opponent_team_id in (home_id, away_id):
                h2h_events.append(event)

        history = []
        for event in h2h_events[:n]:
            event_id = event['id']
            stats_url = f'api/v1/event/{event_id}/player/{player_id}/statistics'
            try:
                stats_data = self.sofascore_request(stats_url)
                if 'statistics' in stats_data:
                    history.append({
                        'match_id': event_id,
                        'match_slug': event.get('slug'),
                        'timestamp': event.get('startTimestamp'),
                        'statistics': stats_data.get('statistics', {})
                    })
            except:
                continue
        return history
