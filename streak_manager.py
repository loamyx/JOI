from datetime import datetime, timedelta
from models import User, Meditation, Achievement, db

class StreakManager:
    @staticmethod
    def calculate_streak(user_id: int) -> tuple[int, bool]:
        """
        Calculate the current streak and whether a new achievement was earned.
        Returns (streak_count, achievement_earned)
        """
        user = User.query.get(user_id)
        if not user:
            return 0, False

        today = datetime.utcnow().date()
        meditations = (Meditation.query
                      .filter_by(user_id=user_id)
                      .order_by(Meditation.completed_at.desc())
                      .all())
        
        if not meditations:
            return 0, False

        current_streak = 1
        last_date = meditations[0].completed_at.date()
        
        # If last meditation wasn't today or yesterday, streak is just today
        if last_date != today and last_date != today - timedelta(days=1):
            return 1, False

        # Count consecutive days
        for i in range(1, len(meditations)):
            curr_date = meditations[i].completed_at.date()
            if last_date - curr_date == timedelta(days=1):
                current_streak += 1
                last_date = curr_date
            else:
                break

        # Update user's streak information
        achievement_earned = False
        if current_streak > user.best_streak:
            user.best_streak = current_streak
            # Check for streak-based achievements
            achievement_earned = StreakManager.check_streak_achievements(user, current_streak)
        
        user.current_streak = current_streak
        db.session.commit()
        
        return current_streak, achievement_earned

    @staticmethod
    def check_streak_achievements(user: User, streak: int) -> bool:
        """Check and award streak-based achievements."""
        streak_achievements = [
            (3, "Three-Day Focus", "Maintain a 3-day meditation streak"),
            (7, "Week of Wisdom", "Complete a full week of daily meditation"),
            (14, "Fortnight of Flow", "Maintain a 2-week meditation streak"),
            (21, "Three Weeks of Tranquility", "Complete 21 days of meditation"),
            (30, "Monthly Master", "Maintain a monthly meditation practice"),
            (100, "Centurion of Calm", "Complete 100 days of meditation"),
        ]

        achievement_earned = False
        for days, title, description in streak_achievements:
            if streak >= days and not Achievement.query.filter_by(
                user_id=user.id, title=title
            ).first():
                new_achievement = Achievement(
                    user_id=user.id,
                    title=title,
                    description=description
                )
                db.session.add(new_achievement)
                achievement_earned = True

        return achievement_earned

    @staticmethod
    def get_weekly_stats(user_id: int) -> list[dict]:
        """Get meditation statistics for the last 7 days."""
        today = datetime.utcnow().date()
        stats = []
        
        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)
            meditations = (Meditation.query
                         .filter_by(user_id=user_id)
                         .filter(db.func.date(Meditation.completed_at) == target_date)
                         .all())
            
            total_minutes = sum(m.duration // 60 for m in meditations)
            stats.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'day': target_date.strftime('%a'),
                'minutes': total_minutes,
                'sessions': len(meditations)
            })
        
        return stats
