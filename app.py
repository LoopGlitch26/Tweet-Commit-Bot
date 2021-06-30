import shutil
from os import path
from datetime import datetime
import twitter
from git import Repo, Commit
import toml

def clone_repo(config_dico):
	print("Cloning from " + config_dico["Repo"]["repo_url"] + " ...")
	return Repo.clone_from(timestamp_str() + config_dico["Repo"]["repo_url"], "repo")

def remove_repo():
	shutil.rmtree('repo')

def repo_openning(config_dico):
	if path.exists("repo"):
		repo = Repo("repo")
		if hasattr(repo.remotes, "origin"):
			if repo.remotes.origin.url == config_dico["Repo"]["repo_url"]:
				print(timestamp_str() + "Pull master head from origin " + config_dico["Repo"]["repo_url"] + " ...")
				repo.remotes.origin.pull()
			else:
				remove_repo()
				repo = clone_repo(config_dico)
		else:
			remove_repo()
			repo = clone_repo(config_dico)
	else:
		repo = clone_repo(config_dico)
	return repo

def format_commit_message(message):
	return commits.message + " " if len(commits.message) < 200 else commits.message[0:200] + " ... "

def timestamp_str():
	return "[" + str(datetime.now()) + "] "

def load_twitter_api(config_dico):
	return twitter.Api(
		consumer_key=config_dico["Twitter"]["consumer_key"],
		consumer_secret=config_dico["Twitter"]["consumer_secret"],
		access_token_key=config_dico["Twitter"]["access_token_key"],
		access_token_secret=config_dico["Twitter"]["access_token_secret"]
		)

print(timestamp_str() + "Script starting ...")

config = toml.load("config.toml")
save = toml.load("save.toml")

api = load_twitter_api(config)
repo = repo_openning(config)

print(timestamp_str() + "Last Commit was : " + save["Commit"]["last_commit"])

commits_list = list(repo.iter_commits('master', max_count=config["Config"]["commit_quantity_check"]))

if commits_list[0].hexsha != save["Commit"]["last_commit"]:
	commits_untweeted = list()

	for commits in commits_list:
		if commits.hexsha != save["Commit"]["last_commit"]:
			commits_untweeted.append(commits)
		else:
			break

	save["Commit"]["last_commit"] = commits_untweeted[0].hexsha
	toml.dump(save, open("save.toml", "w+"))
	
	commits_untweeted.reverse()

	print(timestamp_str() + "Tweeting " + str(len(commits_untweeted)) + " commits ...")

	for commits in commits_untweeted:
		if config["Config"]["fake_run"] == False:
			api.PostUpdate(format_commit_message(commits.message) + repo.remotes.origin.url + "/commit/" + commits.hexsha)
		
		print(format_commit_message(commits.message))
		print("URL : " + repo.remotes.origin.url + "/commit/" + commits.hexsha)
		##
else:
	print(timestamp_str() + "No new commit to tweet")

print(timestamp_str() + "Script Finished.")
