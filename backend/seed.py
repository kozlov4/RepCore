import asyncio
from sqlalchemy import select

# Обязательный импорт всех моделей, чтобы SQLAlchemy увидел ForeignKey
import src.core.models
from src.core.db_helper import db_helper
from src.modules.exercises.models import Exercise, MuscleGroup

# Ровно 100 упражнений
INITIAL_EXERCISES = [
    # --- ГРУДЬ (CHEST) ---
    {"name": "Barbell Bench Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Incline Barbell Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Decline Barbell Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Dumbbell Bench Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Incline Dumbbell Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Decline Dumbbell Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Dumbbell Flyes", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Incline Dumbbell Flyes", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Cable Crossover", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Low Cable Crossover", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Pec Deck Machine", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Machine Chest Press", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": False},
    {"name": "Push-ups", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": True},
    {"name": "Wide Push-ups", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": True},
    {"name": "Diamond Push-ups", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": True},
    {"name": "Spiderman Push-ups", "muscle_group": MuscleGroup.CHEST, "is_bodyweight": True},

    # --- СПИНА (BACK) ---
    {"name": "Pull-ups", "muscle_group": MuscleGroup.BACK, "is_bodyweight": True},
    {"name": "Weighted Pull-ups", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Chin-ups", "muscle_group": MuscleGroup.BACK, "is_bodyweight": True},
    {"name": "Deadlift", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Sumo Deadlift", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Barbell Bent-Over Row", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Dumbbell Row", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "T-Bar Row", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Seated Cable Row", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Lat Pulldown", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Close-Grip Lat Pulldown", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Straight Arm Pulldown", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Face Pulls", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Hyperextension", "muscle_group": MuscleGroup.BACK, "is_bodyweight": True},
    {"name": "Weighted Hyperextension", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Inverted Row", "muscle_group": MuscleGroup.BACK, "is_bodyweight": True},
    {"name": "Machine Row", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},
    {"name": "Dumbbell Pullover", "muscle_group": MuscleGroup.BACK, "is_bodyweight": False},

    # --- НОГИ (LEGS) ---
    {"name": "Barbell Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Front Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Goblet Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Hack Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Leg Press", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Walking Lunges", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Reverse Lunges", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Bulgarian Split Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Romanian Deadlift (RDL)", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Stiff-Leg Deadlift", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Leg Extension", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Seated Leg Curl", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Lying Leg Curl", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Standing Calf Raise", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Seated Calf Raise", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Hip Thrust", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Glute Bridge", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": True},
    {"name": "Step-ups", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Pistol Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": True},
    {"name": "Sumo Squat", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Cable Pull Through", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},
    {"name": "Inner Thigh Machine", "muscle_group": MuscleGroup.LEGS, "is_bodyweight": False},

    # --- ПЛЕЧИ (SHOULDERS) ---
    {"name": "Overhead Press (OHP)", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Seated Dumbbell Press", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Arnold Press", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Lateral Raises", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Cable Lateral Raises", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Front Raises", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Plate Front Raise", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Reverse Dumbbell Flyes", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Reverse Machine Flyes", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Upright Row", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Barbell Shrugs", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Dumbbell Shrugs", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Push Press", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": False},
    {"name": "Handstand Push-ups", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": True},
    {"name": "Pike Push-ups", "muscle_group": MuscleGroup.SHOULDERS, "is_bodyweight": True},

    # --- РУКИ (ARMS) ---
    {"name": "Barbell Bicep Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Dumbbell Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Hammer Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Preacher Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Concentration Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Cable Bicep Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "EZ-Bar Curl", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Triceps Pushdown", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Rope Triceps Pushdown", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Skull Crushers", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Overhead Triceps Extension", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Cable Triceps Extension", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Dumbbell Kickback", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Close-Grip Bench Press", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": False},
    {"name": "Dips", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": True},
    {"name": "Bench Dips", "muscle_group": MuscleGroup.ARMS, "is_bodyweight": True},

    # --- ПРЕСС / КОР (CORE) ---
    {"name": "Plank", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Side Plank", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Crunches", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Decline Crunches", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Bicycle Crunches", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Russian Twists", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Weighted Russian Twists", "muscle_group": MuscleGroup.CORE, "is_bodyweight": False},
    {"name": "Hanging Leg Raises", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Lying Leg Raises", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Ab Wheel Rollout", "muscle_group": MuscleGroup.CORE, "is_bodyweight": False},
    {"name": "Mountain Climbers", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "V-Ups", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Dead Bug", "muscle_group": MuscleGroup.CORE, "is_bodyweight": True},
    {"name": "Cable Crunches", "muscle_group": MuscleGroup.CORE, "is_bodyweight": False},
]

async def seed_100_exercises():
    async with db_helper.session_factory() as session:
        # Проверяем количество записей, чтобы не дублировать
        result = await session.execute(select(Exercise).limit(1))
        if result.scalars().first():
            print("Упражнения уже существуют в базе. Очистите таблицу или удалите проверку.")
            return

        for ex_data in INITIAL_EXERCISES:
            exercise = Exercise(
                name=ex_data["name"],
                muscle_group=ex_data["muscle_group"],
                is_bodyweight=ex_data["is_bodyweight"],
                user_id=None  # Глобальные упражнения, доступные всем
            )
            session.add(exercise)

        await session.commit()
        print(f"Успешно добавлено {len(INITIAL_EXERCISES)} базовых упражнений!")

if __name__ == "__main__":
    asyncio.run(seed_100_exercises())