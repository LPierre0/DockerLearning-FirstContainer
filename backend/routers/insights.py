from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from database import get_db
from models import BodyMeasurement, BodyWeight, User, Workout, WorkoutSet
from schemas import InsightPromptOut

router = APIRouter(prefix="/insights", tags=["insights"])

PERIOD_DAYS = {
    "4w": 28,
    "1m": 30,
    "3m": 91,
    "6m": 183,
}

MEASUREMENT_FIELDS = [
    ("chest_cm", "Poitrine"),
    ("waist_cm", "Taille"),
    ("hips_cm", "Hanches"),
    ("arm_cm", "Bras"),
    ("thigh_cm", "Cuisse"),
    ("calf_cm", "Mollet"),
]


def _parse_template_period(template: str, period: str | None) -> tuple[str, int]:
    if template not in {"weekly", "monthly"}:
        raise HTTPException(status_code=422, detail="template must be weekly or monthly")

    if template == "weekly":
        chosen = period or "4w"
        if chosen != "4w":
            raise HTTPException(status_code=422, detail="weekly template only supports period=4w")
        return chosen, PERIOD_DAYS[chosen]

    chosen = period or "1m"
    if chosen not in {"1m", "3m", "6m"}:
        raise HTTPException(status_code=422, detail="monthly template supports period=1m|3m|6m")
    return chosen, PERIOD_DAYS[chosen]


def _fmt(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def _summarize_weights(entries):
    if not entries:
        return {"count": 0}

    values = [e.weight_kg for e in entries]
    first = values[0]
    last = values[-1]
    return {
        "count": len(values),
        "first": first,
        "last": last,
        "delta": last - first,
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
    }


def _summarize_measurements(entries):
    summary = {}
    for key, _label in MEASUREMENT_FIELDS:
        vals = [getattr(e, key) for e in entries if getattr(e, key) is not None]
        if not vals:
            continue
        summary[key] = {
            "first": vals[0],
            "last": vals[-1],
            "delta": vals[-1] - vals[0] if len(vals) > 1 else None,
            "count": len(vals),
        }
    return summary


def _format_measurement_row(entry: BodyMeasurement) -> str:
    values = []
    for key, label in MEASUREMENT_FIELDS:
        value = getattr(entry, key)
        if value is not None:
            values.append(f"{label}: {value:.1f} cm")
    if not values:
        values = ["aucune valeur"]
    return f"- {entry.logged_at.strftime('%Y-%m-%d')}: " + " | ".join(values)


def _format_set_row(workout_set: WorkoutSet) -> str:
    parts = [
        f"{workout_set.exercise.name} - serie {workout_set.set_number}",
        f"statut={workout_set.status}",
    ]
    if workout_set.weight_kg is not None:
        parts.append(f"charge={_fmt(workout_set.weight_kg)} kg")
    if workout_set.reps is not None:
        parts.append(f"reps={workout_set.reps}")
    if workout_set.rpe is not None:
        parts.append(f"rpe={workout_set.rpe}")
    if workout_set.duration_seconds is not None:
        parts.append(f"duree={int(workout_set.duration_seconds)} sec")
    if workout_set.resistance is not None:
        parts.append(f"resistance={workout_set.resistance}")
    if workout_set.calories is not None:
        parts.append(f"calories={workout_set.calories}")
    if workout_set.notes:
        parts.append(f"note_set={workout_set.notes.strip()}")
    return " | ".join(parts)


def _format_workouts_full_lines(workouts: list[Workout]) -> list[str]:
    if not workouts:
        return ["- Donnees insuffisantes: aucune seance completee sur la periode."]

    lines: list[str] = []
    for workout in workouts:
        completed_at = workout.completed_at.strftime("%Y-%m-%d %H:%M") if workout.completed_at else "n/a"
        title_parts = [f"- Seance #{workout.id}"]
        title_parts.append(f"date={completed_at}")
        title_parts.append(f"type={workout.type}")
        if workout.name:
            title_parts.append(f"nom={workout.name}")
        if workout.notes:
            title_parts.append(f"note={workout.notes.strip()}")
        lines.append(" | ".join(title_parts))

        sorted_sets = sorted(workout.sets, key=lambda s: s.id)
        if not sorted_sets:
            lines.append("  - Aucune serie")
            continue
        for workout_set in sorted_sets:
            lines.append(f"  - {_format_set_row(workout_set)}")
    return lines


@router.get("/prompt", response_model=InsightPromptOut)
def get_insight_prompt(
    user_id: int,
    template: str = "weekly",
    period: str | None = None,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    resolved_period, days = _parse_template_period(template, period)
    now = datetime.utcnow()
    start = now - timedelta(days=days)
    prev_start = start - timedelta(days=days)
    prev_end = start

    weights_current = (
        db.query(BodyWeight)
        .filter(BodyWeight.user_id == user_id, BodyWeight.logged_at >= start, BodyWeight.logged_at < now)
        .order_by(BodyWeight.logged_at.asc())
        .all()
    )
    weights_previous = (
        db.query(BodyWeight)
        .filter(BodyWeight.user_id == user_id, BodyWeight.logged_at >= prev_start, BodyWeight.logged_at < prev_end)
        .order_by(BodyWeight.logged_at.asc())
        .all()
    )
    weight_cur = _summarize_weights(weights_current)
    weight_prev = _summarize_weights(weights_previous)

    meas_current = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user_id, BodyMeasurement.logged_at >= start, BodyMeasurement.logged_at < now)
        .order_by(BodyMeasurement.logged_at.asc())
        .all()
    )
    meas_previous = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user_id, BodyMeasurement.logged_at >= prev_start, BodyMeasurement.logged_at < prev_end)
        .order_by(BodyMeasurement.logged_at.asc())
        .all()
    )
    meas_cur = _summarize_measurements(meas_current)
    meas_prev = _summarize_measurements(meas_previous)

    workouts_current = (
        db.query(Workout)
        .options(joinedload(Workout.sets).joinedload(WorkoutSet.exercise))
        .filter(
            Workout.user_id == user_id,
            Workout.completed_at.isnot(None),
            Workout.completed_at >= start,
            Workout.completed_at < now,
        )
        .order_by(Workout.completed_at.asc())
        .all()
    )
    workouts_previous = (
        db.query(Workout)
        .options(joinedload(Workout.sets).joinedload(WorkoutSet.exercise))
        .filter(
            Workout.user_id == user_id,
            Workout.completed_at.isnot(None),
            Workout.completed_at >= prev_start,
            Workout.completed_at < prev_end,
        )
        .order_by(Workout.completed_at.asc())
        .all()
    )

    weight_lines = []
    if weight_cur.get("count", 0) == 0:
        weight_lines.append("- Donnees insuffisantes: aucune mesure de poids sur la periode.")
    else:
        weight_lines.append(
            f"- Poids: {_fmt(weight_cur['first'])} -> {_fmt(weight_cur['last'])} kg "
            f"(delta {_fmt(weight_cur['delta'])} kg, min {_fmt(weight_cur['min'])}, max {_fmt(weight_cur['max'])}, moyenne {_fmt(weight_cur['avg'])})."
        )
        if weight_prev.get("count", 0) > 0:
            avg_delta = weight_cur["avg"] - weight_prev["avg"]
            weight_lines.append(f"- vs periode precedente: moyenne {_fmt(avg_delta)} kg.")
        else:
            weight_lines.append("- vs periode precedente: donnees insuffisantes.")

    measurement_lines = []
    if not meas_cur:
        measurement_lines.append("- Donnees insuffisantes: aucune mensuration sur la periode.")
    else:
        for key, label in MEASUREMENT_FIELDS:
            if key not in meas_cur:
                continue
            cur = meas_cur[key]
            prev_last = meas_prev.get(key, {}).get("last")
            prev_delta_txt = f", vs periode precedente {_fmt(cur['last'] - prev_last)} cm" if prev_last is not None else ""
            delta_txt = f"delta periode {_fmt(cur['delta'])} cm" if cur["delta"] is not None else "une seule mesure"
            measurement_lines.append(f"- {label}: {_fmt(cur['last'])} cm ({delta_txt}{prev_delta_txt}).")

    full_workout_lines = _format_workouts_full_lines(workouts_current)
    full_workout_prev_lines = _format_workouts_full_lines(workouts_previous)

    raw_weight_lines = [
        f"- {w.logged_at.strftime('%Y-%m-%d')}: {_fmt(w.weight_kg)} kg"
        for w in weights_current[-8:]
    ] or ["- Aucune entree."]
    raw_measurement_lines = [_format_measurement_row(m) for m in meas_current[-5:]] or ["- Aucune entree."]

    prompt = "\n".join(
        [
            "Tu es un coach sportif et analyste de progression.",
            "Analyse les donnees ci-dessous et reponds en francais clair et concret.",
            "",
            "## Contexte",
            f"- Profil: {user.name}",
            f"- Objectif poids: {_fmt(user.target_weight_kg)} kg",
            f"- Template demande: {template}",
            f"- Periode analysee: {resolved_period} ({days} jours) du {start.strftime('%Y-%m-%d')} au {now.strftime('%Y-%m-%d')}",
            "",
            "## Synthese poids",
            *weight_lines,
            "",
            "## Synthese mensurations",
            *measurement_lines,
            "",
            "## Seances completes (periode analysee)",
            *full_workout_lines,
            "",
            "## Seances completes (periode precedente de reference)",
            *full_workout_prev_lines,
            "",
            "## Donnees semi-brutes recentes",
            "Poids (dernieres entrees):",
            *raw_weight_lines,
            "Mensurations (dernieres entrees):",
            *raw_measurement_lines,
            "",
            "## Ta mission",
            "Donne une reponse en 3 parties:",
            "1) Analyse de la progression (forces / stagnations / incoherences).",
            "2) Hypotheses explicatives priorisees (entrainement, recuperation, nutrition, adherence).",
            "3) Avis global sur l'evolution a partir des seances completes, du poids et des mensurations.",
            "",
            "Contrainte: ne rends pas un plan d'action obligatoire.",
            "Si tu proposes des pistes, garde-les optionnelles et non prescriptives.",
            "Si les donnees sont insuffisantes, dis-le explicitement.",
        ]
    )

    return InsightPromptOut(
        template=template,
        period=resolved_period,
        generated_at=now,
        prompt=prompt,
    )
