import polars as pl
from flask import Flask, render_template, request

app = Flask(__name__)

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

    # If both country and year are provided
    if country and year:
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
        return render_template('result1.html', matches=matches)

    elif year:
        filtered_df = df.filter(df['Year'] == int(year))
        matches = filtered_df.select(['Year', 'Stage', 'Home Team Name', 'Home Team Goals', 'Away Team Name', 'Away Team Goals', 'Win conditions']).to_dicts()
        return render_template('result1.html', matches=matches)
        

    # If only one is entered, show error
    return "Error: Please enter both country and year."

if __name__ == '__main__':
    app.run(debug=True)
