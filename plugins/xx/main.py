import datetime

from plugins.xx.crawler import JavLibrary as j1

if __name__ == '__main__':
    proxies = {
        'https': ''
    }
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
    cookie = 'timezone=-480; __qca=P0-560311510-1671015484571; over18=18; __cf_bm=h2.iWK7gRG1DgUAsymrmzI.Y7scFYNwnRrusxOZcep8-1674363571-0-AUCk98DnfNv1eoTI1SMzbMf7+mG6Ee7pdK4caLJ4WHCCLAKIpi7G6Ox0ifVwJJnGmpfWBmcYomFir+aWIMcVuC6ktoh60L0Ltw9l986L0ftn7GxzfxWP8Mf5CjQn8Yn6Qtyd3oXAk9IxqMhsxpo/UEY='
    start = datetime.datetime.now().timestamp()
    library = j1(ua=ua, cookie=cookie, proxies=proxies)
    code_list = library.crawling_top20()
    print(code_list)
    end = datetime.datetime.now().timestamp()
    print(end - start)

    # bus = JavBus(proxies=proxies, ua=ua)
    # course = bus.search_teacher('ABW-312')
    # teacher = bus.crawling_teacher('okq')
    # code = bus.search_by_name('三上悠亜')
    # teachers = bus.get_teachers('ABW-312')
    # teachers = bus.search_all_by_name('三上0')
    # print(teachers)
