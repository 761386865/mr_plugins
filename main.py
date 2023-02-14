import shutil

if __name__ == '__main__':
    shutil.copytree('D:\github_projects\movie-bot-dev\mbot', 'D:\github_projects\mr_plugins\mbot', symlinks=True)
    shutil.copytree('D:\github_projects\movie-bot-api\moviebotapi', 'D:\github_projects\mr_plugins\movie-bot-api', symlinks=True)
    # sock5()
