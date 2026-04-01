class PublishingProvider:
    def publish(self, mp3_path, title, sharing="private", description=None, account=None):
        raise NotImplementedError


PROVIDERS = {
    "soundcloud": "publishing.soundcloud.SoundCloudProvider",
}


def load_provider(name):
    entry = PROVIDERS.get(name)
    if not entry:
        raise Exception(f"Unknown publishing provider '{name}'. Available: {', '.join(PROVIDERS)}")
    module_path, class_name = entry.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)()
