from datetime import datetime, timezone, timedelta, date
from database.connection import Base, engine, SessionLocal
from database.models import User, Run, Goal
from backend.services.auth_service import hash_password
from backend.services.run_service import calculate_pace


def seed_database():
    """Seed sample runner with 6 weeks of realistic running activities and goals."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if demo user exists
        demo_user = db.query(User).filter(User.username == "elite_runner").first()
        if demo_user:
            print("Demo user 'elite_runner' already exists. Cleaning up existing runs/goals...")
            db.query(Run).filter(Run.user_id == demo_user.id).delete()
            db.query(Goal).filter(Goal.user_id == demo_user.id).delete()
            db.commit()
        else:
            print("Creating demo user 'elite_runner'...")
            demo_user = User(
                username="elite_runner",
                email="runner@runtrack.com",
                full_name="Alex Morgan",
                hashed_password=hash_password("RunTrack2026!"),
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

        user_id = demo_user.id
        now = datetime.now()

        # Generate 16 realistic runs across 6 weeks
        sample_activities = [
            # Week 1 (6 weeks ago)
            (40, 5.0, 28.5, 340, 150, 25.0, "Easy recovery jog around the campus"),
            (38, 8.0, 44.0, 560, 158, 45.0, "Morning aerobic base run"),
            (36, 12.0, 67.2, 850, 162, 80.0, "Weekend long steady run"),
            # Week 2 (5 weeks ago)
            (33, 6.0, 33.0, 410, 154, 30.0, "Lunch break tempo intervals"),
            (31, 10.0, 53.0, 680, 160, 65.0, "Progressive pace run"),
            (29, 14.0, 77.0, 990, 164, 110.0, "Sunday scenic trail loop"),
            # Week 3 (4 weeks ago)
            (26, 7.0, 36.4, 480, 156, 40.0, "Fartlek speed play"),
            (24, 10.5, 54.6, 720, 162, 70.0, "Mid-week endurance tempo"),
            (22, 16.0, 84.8, 1120, 166, 130.0, "Half marathon prep long run"),
            # Week 4 (3 weeks ago - slight recovery week)
            (19, 5.5, 29.7, 370, 148, 20.0, "Easy recovery miles"),
            (17, 8.0, 41.6, 550, 155, 50.0, "Rhythm run"),
            (15, 11.0, 58.3, 760, 161, 75.0, "Aerobic conditioning"),
            # Week 5 (2 weeks ago - build peak)
            (12, 7.5, 38.2, 520, 160, 55.0, "Interval workout"),
            (10, 12.0, 61.2, 840, 163, 90.0, "Steady state long run"),
            (8, 21.1, 111.8, 1480, 168, 160.0, "Personal record Half Marathon!"),
            # Week 6 (current week)
            (4, 6.2, 31.0, 430, 152, 35.0, "Post-race easy shakeout"),
            (2, 8.5, 42.5, 590, 159, 55.0, "Aerobic tempo maintenance"),
        ]

        print(f"Inserting {len(sample_activities)} runs for user_id={user_id}...")
        for days_ago, dist, dur, cal, hr, elev, notes in sample_activities:
            run_dt = now - timedelta(days=days_ago, hours=3)
            pace = calculate_pace(dur, dist)
            run_obj = Run(
                user_id=user_id,
                date=run_dt,
                distance_km=dist,
                duration_minutes=dur,
                pace_min_per_km=pace,
                calories=cal,
                avg_heart_rate=hr,
                elevation_gain=elev,
                notes=notes,
            )
            db.add(run_obj)

        # Seed Goals
        print("Inserting sample goals...")
        goal1 = Goal(
            user_id=user_id,
            goal_type="monthly_distance",
            target_value=80.0,
            start_date=date.today() - timedelta(days=15),
            deadline=date.today() + timedelta(days=15),
            is_active=True,
        )
        goal2 = Goal(
            user_id=user_id,
            goal_type="10k",
            target_value=10.0,
            start_date=date.today() - timedelta(days=30),
            deadline=date.today() + timedelta(days=30),
            is_active=True,
        )
        db.add(goal1)
        db.add(goal2)

        db.commit()
        print("✅ Database seeding complete!")
        print("Demo Credentials:")
        print("  Username: elite_runner")
        print("  Password: RunTrack2026!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
