def _normalize(value) -> str:
    return "" if value is None else str(value).strip()


def _escape(text: str) -> str:
    return text.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")


def buildReceiverAddress(
    company=None,
    prename=None,
    surname=None,
    street=None,
    plz=None,
    place=None,
) -> str:
    lines = []

    company = _normalize(company)
    if company:
        lines.append(company)

    person = " ".join(p for p in (_normalize(prename), _normalize(surname)) if p)
    if person:
        lines.append(person)

    street = _normalize(street)
    if street:
        lines.append(street)

    city = " ".join(p for p in (_normalize(plz), _normalize(place)) if p)
    if city:
        lines.append(city)

    if not lines:
        return r"\mbox{}"

    return "\\\\".join(_escape(line) for line in lines)
