from flaskblog import app

#Allows application to run without 
#running "flask run"
if __name__ == '__main__':
	app.run(debug=True)