import os
import glob

from config.settings import DIR


def clear_webassets_cache(cache_dir=DIR.WEBASSETS, max_files=10):
    files = glob.glob(os.path.join(cache_dir, "*"))
    
    if len(files) > max_files:
        files.sort(key=os.path.getmtime)
        
        files_to_remove = len(files) - max_files
        print(f"*********** TOTAL FILES: {len(files)} *****************")
        print("*********************************************")
        
        for file in files[:files_to_remove]:
            os.remove(file)


auth_css = [
    {
        "name": "auth_css",
        "files": [
            "css/settings.css",
            "css/forms_style.css",
            "css/auth/auth_base.css",
            "css/auth/auth.css",
        ],
        "filters": "rcssmin",
        "output": "dist/auth_css.min.css"
    }
]

base_css = [
    {
        "name": "base_css",
        "files": [
            "css/settings.css",
            "css/forms_style.css",
            "css/base.css",
        ],
        "filters": "rcssmin",
        "output": "dist/base_css.min.css"
    }
]

news_css = [
    {
        "name": "all_news_css",
        "files": [
            "css/news/news_base.css",
            "css/news/all.css"
        ],
        "filters": "rcssmin",
        "output": "dist/all_news_css.min.css"
    },
    {
        "name": "news_css",
        "files": [
            "css/news/news_base.css",
            "css/news/news.css"
        ],
        "filters": "rcssmin",
        "output": "dist/news_css.min.css"
    },
    {
        "name": "delete_news_css",
        "files": [
            "css/news/news_base.css",
            "css/news/delete.css"
        ],
        "filters": "rcssmin",
        "output": "dist/delete_news_css.min.css"
    }
]

bakery_css = [
    {
        "name": "bakery_css",
        "files": [
            "css/bakery/bakery_base.css",
            "css/bakery/programs.css",
        ],
        "filters": "rcssmin",
        "output": "dist/bakery_css.min.css"
    },
    {
        "name": "info_css",
        "files": [
            "css/bakery/bakery_base.css",
            "css/bakery/info.css",
            "css/bakery/item_info.css"
        ],
        "filters": "rcssmin",
        "output": "dist/info_css.min.css"
    },
    {
        "name": "programs_css",
        "files": [
            "css/bakery/bakery_base.css",
            "css/bakery/programs.css"
        ],
        "filters": "rcssmin",
        "output": "dist/programs_css.min.css"
    },
    {
        "name": "search_css",
        "files": [
            "css/bakery/bakery_base.css",
            "css/bakery/search.css",
            "css/bakery/programs.css",
            "css/bakery/item_info.css",
        ],
        "filters": "rcssmin",
        "output": "dist/search_css.min.css"
    }
]

schedule_css = [
    {
        "name": "schedule_css",
        "files": [
            "css/schedule/schedule_base.css",
            "css/schedule/day.css",
        ],
        "filters": "rcssmin",
        "output": "dist/schedule_css.min.css"
    },
    {
        "name": "personal_css",
        "files": [
            "css/schedule/schedule_base.css",
            "css/schedule/personal.css",
            "css/schedule/day.css",
        ],
        "filters": "rcssmin",
        "output": "dist/personal_css.min.css"
    },
    {
        "name": "calendar_css",
        "files": [
            "css/schedule/schedule_base.css",
            "css/schedule/calendar.css",
        ],
        "filters": "rcssmin",
        "output": "dist/calendar_css.min.css"
    }
]

admin_css = [
    {
        "name": "admin_css",
        "files": [
            "css/admin/admin_base.css"
        ],
        "filters": "rcssmin",
        "output": "dist/admin_css.min.css"
    }
]

errors_css = [
    {
        "name": "errors_css",
        "files": [
            "css/errors/error_base.css",
        ],
        "filters": "rcssmin",
        "output": "dist/errors_css.min.css"
    }
]

def get_all_css_bundles():
    return auth_css + base_css + admin_css + news_css + bakery_css + errors_css + schedule_css
