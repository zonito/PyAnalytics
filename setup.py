"""PyAnalytics setup script."""

from setuptools import setup

setup(
    name='pyanalytics',
    version='0.0.1',
    packages=['pyanalytics'],

    # metadata for upload to PyPI
    author='Love Sharma',
    author_email='contact@lovesharma.com',
    description=('Google Analytics collection api - now use it in server'
                 ' as well (not just client). You can track your server'
                 ' side  request / API request which are not possible'
                 ' using client js of Google Analytics.'),
    license='MIT',
    keywords='google analytics pyanalytics python track server client api'.split(),
    url='https://github.com/zonito/pyanalytics',  # project homepage
    download_url='https://github.com/zonito/pyanalytics/archive/0.0.1.tar.gz',
    py_modules=['pyanalytics']
)
