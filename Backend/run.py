from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000) # This will start the Flask application on port 5000 with debug mode enabled.