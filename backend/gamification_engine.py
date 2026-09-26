from datetime import date, timedelta
from models import User, db

def update_gamification(user_id, xp_gained=0):
    user = User.query.get(user_id)
    if not user:
        return
    
    today = date.today()
    
    if user.last_activity_date:
        if user.last_activity_date == today - timedelta(days=1):
            # Consecutive day login
            user.current_streak += 1
        elif user.last_activity_date < today - timedelta(days=1):
            # Broken streak
            user.current_streak = 1
    else:
        # First activity ever
        user.current_streak = 1
        
    user.last_activity_date = today
    user.xp += xp_gained
    
    db.session.commit()
    return {'xp': user.xp, 'current_streak': user.current_streak}
