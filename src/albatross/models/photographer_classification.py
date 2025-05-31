class PhotographerClassification:
    def __init__(
        self,
        name: str,
        description: str,
        blurb: str,
        score: int,
        styling: dict[str, str],
        lesson: str,
        video_url: str | None = None,
        video_title: str | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.blurb = blurb
        self.score = score
        self.styling = styling
        self.lesson = lesson
        self.video_url = video_url
        self.video_title = video_title


class Achievement:
    def __init__(
        self,
        name: str,
        styling: dict[str, str],
    ) -> None:
        self.name = name
        self.styling = styling
