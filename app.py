import polars as pl
from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = '001203'
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

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Retrieve user answers
        user_answers = request.form.to_dict()
        score = 0
        results = []

        # Get the quiz questions stored in the session
        for i, q in enumerate(session.get('quiz_questions', [])):
            correct = q["answer"]
            user_answer = user_answers.get(f"question{i}", "").strip()  # Adjust to match the input names
            if user_answer.lower() == correct.lower():
                score += 1
            results.append({
                "question": q["question"],
                "correct": correct,
                "user_answer": user_answer
            })

        # Render results page
        return render_template('quiz_results.html', results=results, score=score, total=len(results))

    # Generate fixed 5 questions: 3 "Who won" and 2 "How many wins"
    years = champion_df['Year'].to_list()
    random_years = random.sample(years, k=5)  # Pick 5 random years for questions
    
    quiz_questions = []

  
    for year in random_years[:3]:
        champion = champion_df.filter(champion_df['Year'] == year)['Champion'].to_list()
        if champion:
            champion = champion[0]
        else:
            continue 
        quiz_questions.append({
            "question": f"Who won the {year} World Cup?",
            "answer": champion
        })

   
    for year in random_years[3:]:
        country = champion_df.filter(champion_df['Year'] == year)['Champion'].to_list()[0]
        # Count how many times the country won the World Cup
        wins = champion_df.filter(champion_df['Champion'] == country).shape[0]
        quiz_questions.append({
            "question": f"How many World Cups did {country} win?",
            "answer": str(wins)
        })

    session['quiz_questions'] = quiz_questions  # Store in session for grading
    return render_template('quiz.html', questions=quiz_questions)
if __name__ == '__main__':
    app.run(debug=True)
