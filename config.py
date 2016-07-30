settings = dict(

	gitlab1 = dict(
    	server = 'http://git.mavencode.com',		# Old gitlab instance
    	access_token = 'R5-daAn9fBGxGTDe6NzR',		# Admin access token
	),
	gitlab2 = dict(
	    server = 'http://code.mavencode.com',		# New gitlab instance
	    access_token = '1AY4qfjooCFyda7zzgvz',		# Admin access token
	),
	default_password = 'changeme',					# Default new password
	total_users  = 100,								# Specify total # of users in old gitlab
	total_groups = 100,								# Specify total # of groups in old gitlab
	total_projects = 100,							# Specify total # of projects in old gitlab
	working_dir = 'old_repos/',						# This is where the old repo will be cloned to
	clean_up = False 								# Delete working directory after migration
)

