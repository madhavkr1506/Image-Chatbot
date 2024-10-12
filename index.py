from wsgi import app

if __name__ == "__main__":
    # Create a temp directory if it doesn't exist to store images    
    app.run(debug=True)