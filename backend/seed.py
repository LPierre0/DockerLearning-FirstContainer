from database import SessionLocal
from models import User, Exercise

PREDEFINED_EXERCISES = [
    # ── Chest ─────────────────────────────────────────────────────────────────
    ("Bench Press", "Chest"),
    ("Incline Bench Press", "Chest"),
    ("Decline Bench Press", "Chest"),
    ("Dumbbell Bench Press", "Chest"),
    ("Incline Dumbbell Press", "Chest"),
    ("Push-Up", "Chest"),
    ("Close-Grip Push-Up", "Chest"),
    ("Dumbbell Fly", "Chest"),
    ("Incline Dumbbell Fly", "Chest"),
    ("Cable Crossover", "Chest"),
    ("Cable Fly (Low)", "Chest"),
    ("Cable Fly (High)", "Chest"),
    ("Chest Dip", "Chest"),
    ("Pec Deck Machine", "Chest"),
    # ── Back ──────────────────────────────────────────────────────────────────
    ("Pull-Up", "Back"),
    ("Chin-Up", "Back"),
    ("Barbell Row", "Back"),
    ("Dumbbell Row", "Back"),
    ("Pendlay Row", "Back"),
    ("Lat Pulldown", "Back"),
    ("Close-Grip Lat Pulldown", "Back"),
    ("Cable Row", "Back"),
    ("Seated Cable Row (Wide)", "Back"),
    ("Deadlift", "Back"),
    ("Rack Pull", "Back"),
    ("T-Bar Row", "Back"),
    ("Straight-Arm Pulldown", "Back"),
    ("Hyperextension", "Back"),
    # ── Legs ──────────────────────────────────────────────────────────────────
    ("Squat", "Legs"),
    ("Front Squat", "Legs"),
    ("Romanian Deadlift", "Legs"),
    ("Sumo Deadlift", "Legs"),
    ("Leg Press", "Legs"),
    ("Hack Squat", "Legs"),
    ("Bulgarian Split Squat", "Legs"),
    ("Lunges", "Legs"),
    ("Walking Lunges", "Legs"),
    ("Leg Curl (Lying)", "Legs"),
    ("Leg Curl (Seated)", "Legs"),
    ("Leg Extension", "Legs"),
    ("Calf Raise (Standing)", "Legs"),
    ("Calf Raise (Seated)", "Legs"),
    ("Hip Thrust", "Legs"),
    ("Glute Kickback", "Legs"),
    ("Adductor Machine", "Legs"),
    ("Abductor Machine", "Legs"),
    # ── Shoulders ─────────────────────────────────────────────────────────────
    ("Overhead Press (Barbell)", "Shoulders"),
    ("Overhead Press (Dumbbell)", "Shoulders"),
    ("Arnold Press", "Shoulders"),
    ("Lateral Raise", "Shoulders"),
    ("Cable Lateral Raise", "Shoulders"),
    ("Face Pull", "Shoulders"),
    ("Front Raise", "Shoulders"),
    ("Upright Row", "Shoulders"),
    ("Reverse Fly", "Shoulders"),
    ("Cable Reverse Fly", "Shoulders"),
    ("Shrugs (Barbell)", "Shoulders"),
    ("Shrugs (Dumbbell)", "Shoulders"),
    # ── Arms ──────────────────────────────────────────────────────────────────
    ("Bicep Curl (Barbell)", "Arms"),
    ("Bicep Curl (Dumbbell)", "Arms"),
    ("Hammer Curl", "Arms"),
    ("Incline Dumbbell Curl", "Arms"),
    ("Cable Bicep Curl", "Arms"),
    ("Preacher Curl", "Arms"),
    ("Concentration Curl", "Arms"),
    ("Tricep Pushdown", "Arms"),
    ("Tricep Pushdown (Rope)", "Arms"),
    ("Skull Crusher", "Arms"),
    ("Overhead Tricep Extension", "Arms"),
    ("Dips", "Arms"),
    ("Close-Grip Bench Press", "Arms"),
    ("Cable Kickback", "Arms"),
    # ── Core ──────────────────────────────────────────────────────────────────
    ("Plank", "Core"),
    ("Side Plank", "Core"),
    ("Ab Crunch", "Core"),
    ("Cable Crunch", "Core"),
    ("Hanging Leg Raise", "Core"),
    ("Knee Raise", "Core"),
    ("Russian Twist", "Core"),
    ("Bicycle Crunch", "Core"),
    ("Ab Wheel Rollout", "Core"),
    ("Decline Crunch", "Core"),
    ("Pallof Press", "Core"),
    ("Woodchop", "Core"),
    # ── Cardio ────────────────────────────────────────────────────────────────
    ("Running", "Cardio"),
    ("Cycling", "Cardio"),
    ("Jump Rope", "Cardio"),
    ("Rowing Machine", "Cardio"),
    ("Ski Erg", "Cardio"),
    ("Stair Climber", "Cardio"),
    ("Elliptical", "Cardio"),
    ("HIIT Sprint", "Cardio"),
    ("Battle Rope", "Cardio"),
]

USERS = [
    {"name": "Pierre", "theme_key": "pierre"},
    {"name": "Lou", "theme_key": "partner"},
]


def seed_initial_data():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            for u in USERS:
                db.add(User(name=u["name"], theme_key=u["theme_key"]))
            db.commit()

        # Add any predefined exercises that aren't already in the DB
        existing_names = {
            name for (name,) in db.query(Exercise.name)
            .filter(Exercise.is_custom == False)
            .all()
        }
        new_exercises = [
            Exercise(name=name, muscle_group=group, is_custom=False)
            for name, group in PREDEFINED_EXERCISES
            if name not in existing_names
        ]
        if new_exercises:
            db.add_all(new_exercises)
            db.commit()
    finally:
        db.close()
