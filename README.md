# gitlab2gitlab
A quick python script to help me copy all my project repositories from one Gitlab instance to another via Gitlab API
http://docs.gitlab.com/ee/api/


## How to use

1. Install the python dependencies 
   `pip install -r requirements.txt`

2. Create Access token with any Admin accounts from both the old
   and new Gitlab servers

3. Update the `config.py` settings

4. Execute the python script
	`./migrator.py`


## Todo

* Add support for other API features 


## Developers
Philip K. Adetiloye - philip@mavencode.com


## Contributors

Suggestions or pull request are welcome
