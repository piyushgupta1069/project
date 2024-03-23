Go to directory of project
Run these command
  python -m venv myenv
  myenv\Scripts\activate (for windows)
  source myenv/bin/activate (for macOs and linux )

  pip install flask flask_sqlalchemy requests celery[redis]

  python app.py

now Open a new terminal or command prompt window, navigate to the same directory, activate the virtual environment (if you created one), and run the Celery worker
  celery -A app.celery worker --loglevel=info


Once the Flask application and Celery worker are running, you can access the API endpoints using a web browser or tools like curl or Postman. The API will be available at http://127.0.0.1:5000/videos.

That's it!
  
