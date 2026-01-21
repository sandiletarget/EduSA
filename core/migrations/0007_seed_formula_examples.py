from django.db import migrations


def seed_formulas(apps, schema_editor):
    Formula = apps.get_model("core", "Formula")

    examples = [
        {
            "grade": 4,
            "subject": "mathematics",
            "topic": "Area of a rectangle",
            "formula_text": "Area = length × width",
            "explanation": "Multiply the length by the width to get the area.",
        },
        {
            "grade": 4,
            "subject": "mathematics",
            "topic": "Perimeter of a rectangle",
            "formula_text": "Perimeter = 2(l + w)",
            "explanation": "Add length and width, then multiply by 2.",
        },
        {
            "grade": 7,
            "subject": "mathematics",
            "topic": "Mean",
            "formula_text": "Mean = sum ÷ number of values",
            "explanation": "Add all values, then divide by how many values there are.",
        },
        {
            "grade": 7,
            "subject": "physical_sciences",
            "topic": "Speed",
            "formula_text": "Speed = distance ÷ time",
            "explanation": "Divide distance traveled by the time taken.",
        },
        {
            "grade": 10,
            "subject": "mathematics",
            "topic": "Quadratic formula",
            "formula_text": "x = (−b ± √(b² − 4ac)) ÷ (2a)",
            "explanation": "Use when solving ax² + bx + c = 0.",
        },
        {
            "grade": 10,
            "subject": "physical_sciences",
            "topic": "Ohm's law",
            "formula_text": "V = I × R",
            "explanation": "Voltage equals current multiplied by resistance.",
        },
        {
            "grade": 10,
            "subject": "accounting",
            "topic": "Gross profit",
            "formula_text": "Gross profit = Sales − Cost of sales",
            "explanation": "Subtract cost of sales from sales revenue.",
        },
        {
            "grade": 12,
            "subject": "mathematics",
            "topic": "Trigonometric identity",
            "formula_text": "sin²θ + cos²θ = 1",
            "explanation": "Fundamental identity for all angles θ.",
        },
        {
            "grade": 12,
            "subject": "physical_sciences",
            "topic": "Newton's second law",
            "formula_text": "F = m × a",
            "explanation": "Force equals mass multiplied by acceleration.",
        },
        {
            "grade": 12,
            "subject": "geography",
            "topic": "Population density",
            "formula_text": "Density = population ÷ land area",
            "explanation": "Divide population by the land area.",
        },
        {
            "grade": 12,
            "subject": "life_sciences",
            "topic": "Magnification",
            "formula_text": "Magnification = image size ÷ actual size",
            "explanation": "Compare the size of the image to the real object.",
        },
    ]

    for item in examples:
        Formula.objects.get_or_create(
            grade=item["grade"],
            subject=item["subject"],
            topic=item["topic"],
            defaults={
                "formula_text": item["formula_text"],
                "explanation": item["explanation"],
            },
        )


def unseed_formulas(apps, schema_editor):
    Formula = apps.get_model("core", "Formula")
    Formula.objects.filter(topic__in=[
        "Area of a rectangle",
        "Perimeter of a rectangle",
        "Mean",
        "Speed",
        "Quadratic formula",
        "Ohm's law",
        "Gross profit",
        "Trigonometric identity",
        "Newton's second law",
        "Population density",
        "Magnification",
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_add_formula_model"),
    ]

    operations = [
        migrations.RunPython(seed_formulas, unseed_formulas),
    ]
