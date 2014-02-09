from setuptools import setup

setup(name='KU EXPO Scoring',
      version='1.0',
      description='KU EXPO Scoring System and Mobile App Backend',
      author='Howard Grimberg',
      author_email='hgrimberg@ku.edu',
      url='https://hgrimberg01@bitbucket.org/hgrimberg01/esc',
      install_requires=['Django==1.4.3','gunicorn','simplejson','mysql-connector-python','django-twilio','reportlab','django-localflavor','django-localflavor-us','django-adminplus'],
     )
