import argparse
import os
from datetime import datetime
from models import Show, ShowPublication
from ..action import Action
from utils import load_config
from publishing.provider import load_provider, PROVIDERS as PUBLISHING_PROVIDERS

config = load_config()


class PublishShowAction(Action):

    def __init__(self, show_id, args):
        self.show_id = show_id
        self.title = args.title
        self.provider_name = args.provider
        self.public = args.public
        self.account = args.account

    def _resolve_title(self, show):
        if self.title:
            return self.title
        template = config.get("PUBLISH_TITLE_TEMPLATE")
        if template:
            date = show.first_air_date.strftime("%-m-%-d-%Y")
            return template.format(date=date, name=show.name)
        return show.name

    def _resolve_description(self, show):
        template = config.get("PUBLISH_DESCRIPTION_TEMPLATE")
        if template:
            date = show.first_air_date.strftime("%B %-d, %Y")
            return template.format(date=date, name=show.name)
        return None

    def run(self):
        show = Show.get_by_id(self.show_id)
        provider = load_provider(self.provider_name)

        existing = (ShowPublication
                    .select()
                    .where(ShowPublication.show == show, ShowPublication.provider == self.provider_name)
                    .order_by(ShowPublication.published_at.desc())
                    .first())

        if existing and self.public:
            title = self._resolve_title(show)
            print(f"Updating '{title}' to public...")
            provider.update_sharing(existing.external_id, "public", account=existing.account)
            print(f"  Track is now public: {existing.url}")
            return

        if not show.is_built:
            raise Exception("Show has not been built yet. Run 'show build' first.")

        if not show.filename:
            raise Exception("Show has no filename. Rebuild the show.")

        show_dir = config.get("SHOW_DIR")
        if not show_dir:
            raise Exception("SHOW_DIR is not set in .env")

        mp3_path = os.path.join(show_dir, show.filename)
        if not os.path.exists(mp3_path):
            raise Exception(f"Built show file not found: {mp3_path}")

        title = self._resolve_title(show)
        description = self._resolve_description(show)
        sharing = "public" if self.public else "private"
        print(f"Publishing '{title}' ({sharing})...")
        result = provider.publish(mp3_path, title, sharing=sharing, description=description, account=self.account)
        ShowPublication.create(
            show=show,
            provider=self.provider_name,
            account=self.account,
            external_id=result["external_id"],
            url=result["url"],
            published_at=datetime.now(),
        )
        print(f"  Saved publication record.")


def handle(args, **kwargs):
    parser = argparse.ArgumentParser(description="Publish a built show to a streaming platform")
    parser.add_argument("show_id", help="Show ID")
    parser.add_argument("--title", type=str, help="Override the track title (default: show name)")
    parser.add_argument("--provider", type=str, default=config.get("PUBLISHING_PROVIDER", "soundcloud"),
                        choices=list(PUBLISHING_PROVIDERS.keys()), help="Publishing provider (default: soundcloud)")
    parser.add_argument("--public", action="store_true", help="Upload as public (default: private)")
    parser.add_argument("--account", type=str, help="Publishing account name (e.g. 'main')")
    parsed_args = parser.parse_args(args)
    action = PublishShowAction(parsed_args.show_id, parsed_args)
    try:
        action.run()
    except Exception as e:
        print("Error: " + str(e))
        exit(2)
