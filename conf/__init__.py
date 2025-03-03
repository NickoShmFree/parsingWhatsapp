from pydantic import BaseModel

from .pl import PlaywrightConf


class AppConf(BaseModel):
    pl: PlaywrightConf = PlaywrightConf()


app_conf = AppConf()
