from flask import Flask, render_template, request
from module import BookRecommendation


app = Flask(__name__)
recommendation = BookRecommendation()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        user_input = request.form['user_input']
        df, message1, message2 = recommendation.predict(user_input) 

        # Modify the 'url' column to include image tags
        df['Picture'] = df.apply(lambda row: f'<img src="{row["Picture"]}" width="100" height="150">', axis=1)

        # Convert the DataFrame to HTML
        df_html = df.to_html(escape=False, index=False)


        return render_template('web.html', 
                                user_input=user_input, 
                                df_html=df_html,
                                message1=message1, 
                                message2=message2
                                )

    return render_template('web.html')

if __name__ == '__main__':
    app.run(debug=True)

