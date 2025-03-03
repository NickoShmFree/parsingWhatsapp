from pydantic import BaseModel


class PlaywrightConf(BaseModel):

    headless: bool = True
    user_data_dir: str = "data_chrome"
