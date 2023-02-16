from jinja2.utils import markupsafe


class MomentJS(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, fmt):
        dt = self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z")
        return markupsafe.Markup(
            f"<script>\nmoment.locale(\"en\");\ndocument.write(moment(\"{dt}\").{fmt});\n</script>")

    def format(self, fmt):
        return self.render(f"format(\"{fmt}\")")

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
