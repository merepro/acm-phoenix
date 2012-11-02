<center><img style="width: 70%" src="http://i.imgur.com/c6RGI.png" /></center>
##ACM Phoenix: A rebirth of the original ACM@UCR website
Hi there, welcome to the official repository for the [ACM@UCR](http://acm.frvl.us). This is where you can go to contribute to the website in whichever way you want. We'd love to have your stylistic and code additions to the site.

##Getting Started
ACM@UCR uses a Python microframework named [Flask](http://flask.pocoo.org/) as a backend for page routing and service. It comes packaged with a templating engine called  [Werkzeug](http://werkzeug.pocoo.org/) that has similar syntax to what you might see in [MustacheJS](http://mustache.github.com/), which allows us to easily modularize our templates.

For the frontend, ACM@UCR takes advantage of modern design frameworks such as [Twitter Bootstrap](http://twitter.github.com/bootstrap/) and [HTML5 Boilerplate](http://html5boilerplate.com/) to attain a crisp, easily-extendable markup and user interface. Look, here's an example:
<img src="http://i.imgur.com/yGYto.png" />

We try our best to conform to good coding standards in HTML5/CSS, Javascript, and Python to make sure that future generations will be able to maintain and extend the website as they see fit to add new content.

Personally, I suggest you freshen up on your Python, HTML5/CSS, and Javascript to make sure you can easily read through and understand the code for the most part. The newly founded [webplatform.org](http://www.webplatform.org) will become a good place for HTML5/CSS and Javascript. For Python, I recommend looking through the [Google Python course](http://code.google.com/edu/languages/google-python-class/).

##Ok, cool. So how do I contribute?
Well, first off, make sure your [github account is set up](https://help.github.com/articles/set-up-git). Then fork the repository and make a local clone.

###Setting up the environment
The easiest way to use Python-related projects is to use `pip`. And the easiest way to use `pip` on your personal machine is through [virtualenv](http://pypi.python.org/pypi/virtualenv). Get and set up your virtual environment by running from command line:

    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py my_new_env
    $ . my_new_env/bin/activate

This will create a virtual environment for you. Make sure that when you're developing in the future that you do everything from your virtual environment or you won't have the appropriate dependencies.

Once you're in your virtual environment, navigate to the acm-phoenix directory and run:

    (my_new_env)$ ./configure

This will install all necessary dependencies for the website and also create the database from SQL-Alchemy's schema.

To get the website running on localhost, you can now simply run:

    $ python run.py

If all went well, you should see: 

     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

You can then point your browser to the above URL and you'll have access to a functioning version of the site.

As you access pages, this will spit out all information about requests made and results returned which is basically terminal spam. I recommend you run the Flask instance in the background by redirecting output:

    $ python run.py 2> /path/to/logs/acm-phoenix.log &

This will make it alot easier to debug the application when something goes wrong.

###Technologies used
