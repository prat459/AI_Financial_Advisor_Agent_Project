def safety_check(query):
    banned_keywords = [
        "illegal",
        "tax evasion",
        "fraud",
        "insider trading"
    ]

    for word in banned_keywords:
        if word in query.lower():
            return False

    return True
