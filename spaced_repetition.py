from datetime import datetime, timedelta

def calculate_next_review(difficulty):
    today = datetime.now()
    if difficulty == 1:
        return today + timedelta(days=1)
    elif difficulty == 2:
        return today + timedelta(days=3)
    elif difficulty == 3:
        return today + timedelta(days=7)
    elif difficulty == 4:
        return today + timedelta(days=14)
    else:
        return today + timedelta(days=30)
