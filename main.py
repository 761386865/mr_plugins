import shutil

if __name__ == '__main__':
    shutil.copytree('D:\githubProjects\movie-bot-dev\mbot', 'D:\githubProjects\mr_plugins\mbot', symlinks=True)
    shutil.copytree('D:\githubProjects\movie-bot-api\moviebotapi', 'D:\githubProjects\mr_plugins\movie-bot-api', symlinks=True)
