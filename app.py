import polars as pl
from flask import Flask, render_template, request

app = Flask(__name__)
champion_df = pl.read_csv('data/world_cup.csv')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    country = request.args.get('country')
    year = request.args.get('year')
    if year:
        year = int(year)
        if year < 1930 or year % 4 != 2 or year == 1942 or year == 1946:
            return "No World Cup held in this year."
    # Load the CSV file
    df = pl.read_csv('data/WorldCupMatches.csv')
    df = df.unique(maintain_order=True)
    # If both country and year are provided
    if country and year:
        country1 = country.capitalize()
        # Convert country to lowercase for case-insensitive comparison
        country = country.lower()
        
        # Filter for both country and year
        filtered_df = df.filter(
            ((df['Home Team Name'].str.to_lowercase().str.contains(country)) | 
            (df['Away Team Name'].str.to_lowercase().str.contains(country))) &
            (df['Year'] == int(year))
        )
        if filtered_df.is_empty():
            return f"{country.capitalize()} did not participate in the World Cup in {year}."
        # Prepare the matches for display
        matches = filtered_df.select(['Year', 'Stage', 'Home Team Name', 'Home Team Goals', 'Away Team Name', 'Away Team Goals', 'Win conditions']).to_dicts()
        # Render the result
        return render_template('result1.html', matches=matches, title=f"Year: {year}, Country: {country1}")

    elif year:
        filtered_df = df.filter(df['Year'] == int(year))
        matches = filtered_df.select(['Year', 'Stage', 'Home Team Name', 'Home Team Goals', 'Away Team Name', 'Away Team Goals', 'Win conditions']).to_dicts()
        champion_row = champion_df.filter(champion_df['Year'] == year).select(['Champion', 'photo']).to_dicts()
        champion = champion_row[0]['Champion'] if champion_row else "Unknown"
        photo = champion_row[0]['photo'] if champion_row else None

        return render_template('result2.html', matches=matches, title=f"Year: {year}", champion=champion, photo=photo)

    elif country:
        country = country.lower()
        # Get years of participation
        participated_years = (
            df.filter((df['Home Team Name'].str.to_lowercase().str.contains(country)) | (df['Away Team Name'].str.to_lowercase().str.contains(country))).select('Year').unique().sort(by='Year').to_series().to_list())


        # Calculate matches played
        home_matches = df.filter(df['Home Team Name'].str.to_lowercase().str.contains(country))
        away_matches = df.filter(df['Away Team Name'].str.to_lowercase().str.contains(country))
        total_matches = home_matches.height + away_matches.height
        if total_matches == 0:
            return f"Country: {country.capitalize()} has never participated in a World Cup."

        num_championships = champion_df.filter(champion_df['Champion'].str.to_lowercase().str.contains(country)).height

        return render_template(
            'result3.html',
            title=f"Country: {country.capitalize()}",
            matches_played=total_matches,
            num_champions=num_championships,
            years=participated_years
        )

    return "Error: Please enter year or country for searching."

@app.route('/search_two_countries', methods=['GET'])
def search_two_countries():
    country1 = request.args.get('country1')
    country2 = request.args.get('country2')

    country1 = country1.lower()
    country2 = country2.lower()

    df = pl.read_csv('data/WorldCupMatches.csv')
    
    # Filter for matches between the two countries
    filtered_df = df.filter(
        ((df['Home Team Name'].str.to_lowercase().str.contains(country1)) & (df['Away Team Name'].str.to_lowercase().str.contains(country2))) | 
        ((df['Home Team Name'].str.to_lowercase().str.contains(country2)) & (df['Away Team Name'].str.to_lowercase().str.contains(country1)))
    )
    
    if filtered_df.is_empty():
        return f"No matches found between {country1.capitalize()} and {country2.capitalize()}."
    
    matches = filtered_df.select(['Year', 'Stage', 'Home Team Name', 'Home Team Goals', 'Away Team Name', 'Away Team Goals', 'Win conditions']).to_dicts()

    return render_template('result4.html', matches=matches, country1=country1.capitalize(), country2=country2.capitalize())
if __name__ == '__main__':
    app.run(debug=True)
